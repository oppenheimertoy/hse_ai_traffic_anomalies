import { Box, Center, Text } from "@chakra-ui/react"
import { AnalyzedFileResult, IsolationForestResult } from "../main/types/analyzedFile"
import ReactECharts, { EChartsOption } from "echarts-for-react"
type ChartsContainerProps = {
  result: AnalyzedFileResult
}

export const ChartsContainer: React.FC<ChartsContainerProps> = ({
  result
}) => {
  return <Box

  >
    {result.isolationForest !== undefined && <IsolationForestCharts data={result.isolationForest} />}
  </Box>
}

type IsolationForestChartProps = {
  data: IsolationForestResult
}
const IsolationForestCharts: React.FC<IsolationForestChartProps> = ({
  data,
}) => {
  const anomaliesOptions: EChartsOption = {

    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.anomalies.map((el, index) => index)
    },
    yAxis: {
      type: 'value'
    },
    series: {
      data: data.anomalies,
      type: 'bar'
    },
  }
  const anomalyScoresOptions: EChartsOption = {

    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.anomalyScores.map((el, index) => index)
    },
    yAxis: {
      type: 'value'
    },
    series: {
      data: data.anomalyScores,
      type: 'line'
    },
  }
  return <Box
    w='800px'
    h='600px'
  >
    <Center>
      <Text fontWeight={'bold'}>Anomalies</Text>
    </Center>

    <ReactECharts option={anomaliesOptions} />

    <Center>
      <Text fontWeight={'bold'}>Anomalies Scores</Text>
    </Center>


    <ReactECharts option={anomalyScoresOptions} />
  </Box>
}