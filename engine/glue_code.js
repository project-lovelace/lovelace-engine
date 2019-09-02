var timeStart = process.hrtime();
var userOutput = {:s};
var timeDiff = process.hrtime(timeStart);
var runTime = timeDiff[0] + (timeDiff[1] / 1e9);

var maxMemoryUsage = 0;

var submissionData = {{
  "userOutput": userOutput,
  "runTime": runTime,
  "maxMemoryUsage": maxMemoryUsage
}};  // Double braces to avoid interfering with Python brace-based string formatting.

var fs = require('fs');
var data = JSON.stringify(submissionData);
fs.writeFileSync('{:s}', data);