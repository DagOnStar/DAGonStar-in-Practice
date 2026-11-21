#!/usr/bin/env cwl-runner
# A CWL v1.2 tool: count the data records of a CSV file (every line but the header).
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [awk, "END {print NR - 1}"]
inputs:
  observations:
    type: File
    inputBinding: {position: 1}
stdout: records.txt
outputs:
  records:
    type: File
    outputBinding: {glob: records.txt}
