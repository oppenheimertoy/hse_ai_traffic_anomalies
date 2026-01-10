export const bytesToKilobytes = (bytes: number) => {
  return (bytes / 1000).toFixed(2) + "KB"
}

export const bytesToMegabytes = (bytes: number) => {
  return (bytes / 1000 / 1000).toFixed(2) + "MB"
}