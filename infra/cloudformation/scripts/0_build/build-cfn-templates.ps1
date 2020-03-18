Param (
    [string]$AwsProfile,
    [string]$AwsRegion,
    [string]$StackName,
    [string]$OutputPath = [IO.Path]::Combine((Get-Item $PSScriptRoot).Parent.Parent.FullName, "build-output"),
    [Boolean]$Verbose = $false
)

$envDefaultProfile = $env:AWS_DEFAULT_PROFILE
$envDefaultRegion = $env:AWS_DEFAULT_REGION
$envDefaultPythonPath = $env:PYTHONPATH

$rootDir = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$blueprintsDirPath = [IO.Path]::Combine($rootDir, "blueprints")
$stackerBuketYamlPath = [IO.Path]::Combine($rootDir, "stacker-bucket.yml")
$stackerYamlPath = [IO.Path]::Combine($rootDir, "stacker.yml")
$confDirPath = [IO.Path]::Combine($rootDir, "conf")
$envConfs = Get-ChildItem -Path $confDirPath -Recurse -File `
    | Where-Object { $_.Extension -eq ".env" } `
    | Where-Object { $_.BaseName -ne "local" } `
    | ForEach-Object { $_.FullName }

$env:PYTHONPATH = $blueprintsDirPath

Function DetermineRegion
{
    if ($AwsRegion)
    {
        $env:AWS_DEFAULT_REGION = $AwsRegion
    }
    elseif ($AwsProfile)
    {
        $env:AWS_DEFAULT_PROFILE = $AwsProfile
    }
    elseif ([string]::IsNullOrWhiteSpace($envDefaultProfile) -and [string]::IsNullOrWhiteSpace($envDefaultRegion))
    {
        Write-Host "======= Can't determine region, defaulting to us-east-1 ======="
        $env:AWS_DEFAULT_REGION = "us-east-1"
    }
}

Function ResetEnvironmentVariables
{
    $env:AWS_DEFAULT_PROFILE = $envDefaultProfile
    $env:AWS_DEFAULT_REGION = $envDefaultRegion
    $env:PYTHONPATH = $envDefaultPythonPath
}

Function BuildStackerBucketCommand
{
    $buildStackerBucketCommand = New-Object System.Text.StringBuilder
    [void]$buildStackerBucketCommand.Append("stacker build ")
    [void]$buildStackerBucketCommand.Append("-d $OutputPath ")
    if ($Verbose)
    {
        [void]$buildStackerBucketCommand.Append("-v ")
    }
    [void]$buildStackerBucketCommand.Append("$envConf $stackerBuketYamlPath")
    return $buildStackerBucketCommand.ToString()
}

Function BuildStackerCommand
{
    $buildStackerCommand = New-Object System.Text.StringBuilder
    [void]$buildStackerCommand.Append("stacker build ")
    [void]$buildStackerCommand.Append("-d $OutputPath ")
    if ($Verbose)
    {
        [void]$buildStackerCommand.Append("-v -v ")
    }
    if ($StackName)
    {
        [void]$buildStackerCommand.Append("-stacks $StackName ")
    }
    [void]$buildStackerCommand.Append("$envConf $stackerYamlPath")
    return $buildStackerCommand.ToString()
}

Function GenerateJsonTemplates
{
    foreach ($envConf in $envConfs)
    {
        $envName = [IO.Path]::GetFileNameWithoutExtension($envConf)

        Write-Host "======= Generating templates for $envName ======="

        $buildStackerBucketCommand = BuildStackerBucketCommand
        Write-Host "======= Executing ""$buildStackerBucketCommand"""
        Invoke-Expression -Command "$buildStackerBucketCommand"
        if ($LastExitCode -ne 0)
        {
            throw "Error executing ""$buildStackerBucketCommand"""
        }

        $buildStackerCommand = BuildStackerCommand
        Write-Host "======= Executing ""$buildStackerCommand"""
        Invoke-Expression -Command "$buildStackerCommand"
        if ($LastExitCode -ne 0)
        {
            throw "Error executing ""$buildStackerCommand"""
        }
    }
}

Function ConvertTemplatesToYml
{
    Write-Host "======= Converting templates to YML ======="

    $templatePath = [IO.Path]::Combine($OutputPath, "stack_templates")
    $templateSubDirPaths = Get-ChildItem -Path $templatePath -Recurse -Directory `
        | ForEach-Object { $_.FullName }

    foreach ($path in $templateSubDirPaths)
    {
        $file = Get-ChildItem $path -Filter *.json | Select-Object -First 1
        $subDirName = (Get-Item $file.FullName).Directory.Name
        $outputFile = [IO.Path]::Combine($OutputPath, "$subDirName.yml")
        cfn-flip -c $file.FullName $outputFile
        Write-Host $outputFile
    }

    Remove-Item -LiteralPath $templatePath -Force -Recurse
}

try
{
    DetermineRegion
    GenerateJsonTemplates
    ConvertTemplatesToYml
    ResetEnvironmentVariables
}
catch [Exception]
{
    Write-Host "======= $($_.Exception.Message)"
    ResetEnvironmentVariables
    exit 1
}