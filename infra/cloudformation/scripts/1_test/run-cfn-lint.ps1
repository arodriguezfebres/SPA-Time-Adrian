$rootDir = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$buildOutputDir = [IO.Path]::Combine($rootDir, "build-output")
$cfnLintRcDir = [IO.Path]::Combine($rootDir, ".configrc")
$testOutputDir = [System.IO.Path]::Combine($rootDir, "test-output")

if (-not $($testOutputDir | Test-Path))
{
    New-Item -ItemType directory -Path $testOutputDir
}

$currentLocation = (Get-Location).Path
Set-Location -Path $cfnLintRcDir
cfn-lint --verbose $buildOutputDir/*.yml 2>&1 | Tee-Object -FilePath $testOutputDir/cfn_lint_output.txt
Set-Location -Path $currentLocation