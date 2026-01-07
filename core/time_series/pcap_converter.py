from __future__ import annotations

import socket
from collections import defaultdict
from typing import Dict, List

import dpkt
import numpy as np
import pandas as pd


class PCAPConverter:
    """
    Конвертер PCAP файлов в оконные признаки для временных рядов
    """
    def __init__(self, window_size: int = 1):
        self.window_size = window_size

    def convert(self, pcap_path: str, label: str = "unknown") -> pd.DataFrame:
        """_summary_

        Args:
            pcap_path (str): _description_
            label (str, optional): _description_. Defaults to "unknown".

        Returns:
            pd.DataFrame: _description_
        """
        print(f"processing {pcap_path}")

        windows: Dict[int, List[Dict]] = {}
        base_time: float | None = None
        packet_count = 0
        error_count = 0

        try:
            with open(pcap_path, "rb") as f:
                try:
                    pcap = dpkt.pcap.Reader(f)
                except ValueError:
                    f.seek(0)
                    pcap = dpkt.pcapng.Reader(f)
                for ts, buf in pcap:
                    try:
                        if base_time is None:
                            base_time = ts
                        window_idx = int((ts - base_time) / self.window_size)
                        if window_idx not in windows:
                            windows[window_idx] = []
                        info = self._extract_packet_info(buf, ts)
                        windows[window_idx].append(info)
                        packet_count += 1
                    except Exception:
                        error_count += 1
        except Exception as e:
            print(f"error reading pcap: {e}")
        if packet_count == 0:
            print("no packets extracted")
            return pd.DataFrame()

        print(f"  packets: {packet_count}, errors: {error_count}")

        rows = []
        prev_window_features = None
        for idx in sorted(windows.keys()):
            packets = windows[idx]
            window_start = base_time + idx * self.window_size
            features = self._compute_features(packets, window_start, prev_window_features)
            features["label"] = label
            rows.append(features)
            prev_window_features = features

        df = pd.DataFrame(rows)
        df = self._fill_gaps(df)
        df = self._add_derived_features(df)

        print(f"  windows: {len(df)}")
        return df

    def _extract_packet_info(self, buf: bytes, ts: float) -> Dict:
        """_summary_

        Args:
            buf (bytes): _description_
            ts (float): _description_

        Returns:
            Dict: _description_
        """
        info = {
            "timestamp": ts,
            "length": len(buf),
            "protocol": "other",
            "src_ip": None,
            "dst_ip": None,
            "src_port": None,
            "dst_port": None,
            "flags": {},
            "ttl": None,
            "ip_len": None,
            "payload_len": 0,
        }

        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data

            if isinstance(ip, dpkt.ip.IP):
                info["src_ip"] = socket.inet_ntoa(ip.src)
                info["dst_ip"] = socket.inet_ntoa(ip.dst)
                info["ttl"] = ip.ttl
                info["ip_len"] = ip.len
                transport = ip.data

                if isinstance(transport, dpkt.tcp.TCP):
                    info["protocol"] = "tcp"
                    info["src_port"] = transport.sport
                    info["dst_port"] = transport.dport
                    info["payload_len"] = len(transport.data)
                    info["flags"] = {
                        "syn": bool(transport.flags & dpkt.tcp.TH_SYN),
                        "ack": bool(transport.flags & dpkt.tcp.TH_ACK),
                        "fin": bool(transport.flags & dpkt.tcp.TH_FIN),
                        "rst": bool(transport.flags & dpkt.tcp.TH_RST),
                        "psh": bool(transport.flags & dpkt.tcp.TH_PUSH),
                        "urg": bool(transport.flags & dpkt.tcp.TH_URG),
                    }
                elif isinstance(transport, dpkt.udp.UDP):
                    info["protocol"] = "udp"
                    info["src_port"] = transport.sport
                    info["dst_port"] = transport.dport
                    info["payload_len"] = len(transport.data) if transport.data else 0
                elif isinstance(transport, dpkt.icmp.ICMP):
                    info["protocol"] = "icmp"

            elif isinstance(ip, dpkt.ip6.IP6):
                info["src_ip"] = socket.inet_ntop(socket.AF_INET6, ip.src)
                info["dst_ip"] = socket.inet_ntop(socket.AF_INET6, ip.dst)
                info["ttl"] = ip.hlim
                transport = ip.data

                if isinstance(transport, dpkt.tcp.TCP):
                    info["protocol"] = "tcp"
                    info["src_port"] = transport.sport
                    info["dst_port"] = transport.dport
                    info["payload_len"] = len(transport.data)
                    info["flags"] = {
                        "syn": bool(transport.flags & dpkt.tcp.TH_SYN),
                        "ack": bool(transport.flags & dpkt.tcp.TH_ACK),
                        "fin": bool(transport.flags & dpkt.tcp.TH_FIN),
                        "rst": bool(transport.flags & dpkt.tcp.TH_RST),
                        "psh": bool(transport.flags & dpkt.tcp.TH_PUSH),
                        "urg": bool(transport.flags & dpkt.tcp.TH_URG),
                    }
                elif isinstance(transport, dpkt.udp.UDP):
                    info["protocol"] = "udp"
                    info["src_port"] = transport.sport
                    info["dst_port"] = transport.dport
                    info["payload_len"] = len(transport.data) if transport.data else 0

        except Exception:
            pass

        return info

    def _compute_features(self, packets: List[Dict], window_start: float, 
                          prev_features: Dict | None) -> Dict:
        """вычисление признаков для окна"""
        if not packets:
            return self._empty_features(window_start)

        df = pd.DataFrame(packets)
        n = len(df)
        timestamps = df["timestamp"].values

        # === базовые счётчики ===
        features = {
            "timestamp": pd.Timestamp(window_start, unit="s"),
            "packet_count": n,
            "byte_count": int(df["length"].sum()),
            "payload_bytes": int(df["payload_len"].sum()),
        }

        # === статистики размеров ===
        features["avg_packet_size"] = float(df["length"].mean())
        features["std_packet_size"] = float(df["length"].std()) if n > 1 else 0.0
        features["min_packet_size"] = int(df["length"].min())
        features["max_packet_size"] = int(df["length"].max())
        features["median_packet_size"] = float(df["length"].median())

        # === inter-arrival time (IAT) - ВАЖНО для аномалий ===
        if n > 1:
            iats = np.diff(sorted(timestamps))
            features["iat_mean"] = float(np.mean(iats))
            features["iat_std"] = float(np.std(iats))
            features["iat_min"] = float(np.min(iats))
            features["iat_max"] = float(np.max(iats))
            features["iat_median"] = float(np.median(iats))
            # коэффициент вариации IAT - хороший индикатор burst-ов
            features["iat_cv"] = features["iat_std"] / features["iat_mean"] if features["iat_mean"] > 0 else 0.0
        else:
            features["iat_mean"] = 0.0
            features["iat_std"] = 0.0
            features["iat_min"] = 0.0
            features["iat_max"] = 0.0
            features["iat_median"] = 0.0
            features["iat_cv"] = 0.0

        # === уникальные адреса/порты ===
        features["unique_src_ips"] = int(df["src_ip"].nunique())
        features["unique_dst_ips"] = int(df["dst_ip"].nunique())
        features["unique_src_ports"] = int(df["src_port"].nunique())
        features["unique_dst_ports"] = int(df["dst_port"].nunique())
        
        # уникальные пары (flow-like)
        features["unique_flows"] = int(df.groupby(["src_ip", "dst_ip", "src_port", "dst_port"]).ngroups)
        features["unique_ip_pairs"] = int(df.groupby(["src_ip", "dst_ip"]).ngroups)

        # === протоколы ===
        proto = df["protocol"].value_counts()
        features["tcp_count"] = int(proto.get("tcp", 0))
        features["udp_count"] = int(proto.get("udp", 0))
        features["icmp_count"] = int(proto.get("icmp", 0))
        features["other_proto_count"] = n - features["tcp_count"] - features["udp_count"] - features["icmp_count"]
        features["tcp_ratio"] = features["tcp_count"] / n
        features["udp_ratio"] = features["udp_count"] / n

        # === TCP флаги ===
        tcp_df = df[df["protocol"] == "tcp"]
        if not tcp_df.empty:
            flags_list = tcp_df["flags"].tolist()
            features["syn_count"] = sum(f.get("syn", False) for f in flags_list)
            features["ack_count"] = sum(f.get("ack", False) for f in flags_list)
            features["fin_count"] = sum(f.get("fin", False) for f in flags_list)
            features["rst_count"] = sum(f.get("rst", False) for f in flags_list)
            features["psh_count"] = sum(f.get("psh", False) for f in flags_list)
            features["urg_count"] = sum(f.get("urg", False) for f in flags_list)
            
            # syn без ack - потенциальный scan
            features["syn_only_count"] = sum(
                f.get("syn", False) and not f.get("ack", False) for f in flags_list
            )
            # rst ratio - индикатор проблем/атак
            features["rst_ratio"] = features["rst_count"] / len(tcp_df)
        else:
            for flag in ["syn", "ack", "fin", "rst", "psh", "urg", "syn_only"]:
                features[f"{flag}_count"] = 0
            features["rst_ratio"] = 0.0

        # === TTL статистики ===
        ttl_vals = df["ttl"].dropna()
        if not ttl_vals.empty:
            features["ttl_mean"] = float(ttl_vals.mean())
            features["ttl_std"] = float(ttl_vals.std()) if len(ttl_vals) > 1 else 0.0
            features["ttl_unique"] = int(ttl_vals.nunique())
        else:
            features["ttl_mean"] = 0.0
            features["ttl_std"] = 0.0
            features["ttl_unique"] = 0

        # === порты ===
        well_known_ports = {20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995}
        dst_ports = df["dst_port"].dropna().astype(int)
        if not dst_ports.empty:
            features["well_known_port_ratio"] = sum(p in well_known_ports for p in dst_ports) / len(dst_ports)
            features["high_port_ratio"] = sum(p > 1024 for p in dst_ports) / len(dst_ports)
        else:
            features["well_known_port_ratio"] = 0.0
            features["high_port_ratio"] = 0.0

        # === энтропии ===
        features["entropy_src_ip"] = self._entropy(df["src_ip"])
        features["entropy_dst_ip"] = self._entropy(df["dst_ip"])
        features["entropy_src_port"] = self._entropy(df["src_port"])
        features["entropy_dst_port"] = self._entropy(df["dst_port"])
        features["entropy_length"] = self._entropy(df["length"])

        # === направление трафика (in/out ratio) ===
        # предполагаем что первый IP в окне - "наш" хост
        if not df["src_ip"].empty:
            first_src = df["src_ip"].iloc[0]
            if first_src:
                features["outbound_ratio"] = (df["src_ip"] == first_src).mean()
                features["inbound_ratio"] = (df["dst_ip"] == first_src).mean()
            else:
                features["outbound_ratio"] = 0.5
                features["inbound_ratio"] = 0.5
        else:
            features["outbound_ratio"] = 0.5
            features["inbound_ratio"] = 0.5

        return features

    def _entropy(self, series: pd.Series) -> float:
        """энтропия Шеннона"""
        series = series.dropna()
        if series.empty or series.nunique() <= 1:
            return 0.0
        probs = series.value_counts(normalize=True)
        return float(-np.sum(probs * np.log2(probs)))

    def _empty_features(self, window_start: float) -> Dict:
        """пустые признаки для окна без пакетов"""
        return {
            "timestamp": pd.Timestamp(window_start, unit="s"),
            "packet_count": 0,
            "byte_count": 0,
            "payload_bytes": 0,
            "avg_packet_size": 0.0,
            "std_packet_size": 0.0,
            "min_packet_size": 0,
            "max_packet_size": 0,
            "median_packet_size": 0.0,
            "iat_mean": 0.0,
            "iat_std": 0.0,
            "iat_min": 0.0,
            "iat_max": 0.0,
            "iat_median": 0.0,
            "iat_cv": 0.0,
            "unique_src_ips": 0,
            "unique_dst_ips": 0,
            "unique_src_ports": 0,
            "unique_dst_ports": 0,
            "unique_flows": 0,
            "unique_ip_pairs": 0,
            "tcp_count": 0,
            "udp_count": 0,
            "icmp_count": 0,
            "other_proto_count": 0,
            "tcp_ratio": 0.0,
            "udp_ratio": 0.0,
            "syn_count": 0,
            "ack_count": 0,
            "fin_count": 0,
            "rst_count": 0,
            "psh_count": 0,
            "urg_count": 0,
            "syn_only_count": 0,
            "rst_ratio": 0.0,
            "ttl_mean": 0.0,
            "ttl_std": 0.0,
            "ttl_unique": 0,
            "well_known_port_ratio": 0.0,
            "high_port_ratio": 0.0,
            "entropy_src_ip": 0.0,
            "entropy_dst_ip": 0.0,
            "entropy_src_port": 0.0,
            "entropy_dst_port": 0.0,
            "entropy_length": 0.0,
            "outbound_ratio": 0.5,
            "inbound_ratio": 0.5,
        }

    def _fill_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """заполнение пропущенных окон"""
        if df.empty or len(df) < 2:
            return df

        df = df.set_index("timestamp")
        freq = f"{self.window_size}s"
        full_idx = pd.date_range(df.index.min(), df.index.max(), freq=freq)

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        non_numeric = [c for c in df.columns if c not in numeric_cols]

        df = df.reindex(full_idx)

        for col in numeric_cols:
            df[col] = df[col].fillna(0)

        for col in non_numeric:
            mode = df[col].mode()
            fill_val = mode.iloc[0] if not mode.empty else "unknown"
            df[col] = df[col].fillna(fill_val)

        df.index.name = "timestamp"
        return df.reset_index()

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """добавление производных признаков (лаги, скользящие средние, изменения)"""
        if df.empty or len(df) < 3:
            return df

        # ключевые метрики для временных рядов
        key_cols = ["packet_count", "byte_count", "unique_flows", "entropy_dst_ip"]
        
        for col in key_cols:
            if col not in df.columns:
                continue
                
            # изменение относительно предыдущего окна
            df[f"{col}_diff"] = df[col].diff().fillna(0)
            
            # процентное изменение
            df[f"{col}_pct_change"] = df[col].pct_change().fillna(0).replace([np.inf, -np.inf], 0)
            
            # скользящее среднее (5 окон)
            df[f"{col}_ma5"] = df[col].rolling(5, min_periods=1).mean()
            
            # отклонение от скользящего среднего
            df[f"{col}_ma5_dev"] = df[col] - df[f"{col}_ma5"]
            
            # скользящее стандартное отклонение
            df[f"{col}_rolling_std"] = df[col].rolling(5, min_periods=1).std().fillna(0)

        # burst detection: резкий рост packet_count
        if "packet_count" in df.columns:
            mean_pc = df["packet_count"].mean()
            std_pc = df["packet_count"].std()
            if std_pc > 0:
                df["packet_count_zscore"] = (df["packet_count"] - mean_pc) / std_pc
            else:
                df["packet_count_zscore"] = 0.0

        return df