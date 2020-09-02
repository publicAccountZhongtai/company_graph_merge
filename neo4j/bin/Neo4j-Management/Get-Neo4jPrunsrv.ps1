# Copyright (c) 2002-2018 "Neo4j,"
# Neo4j Sweden AB [http://neo4j.com]
#
# This file is part of Neo4j.
#
# Neo4j is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


<#
.SYNOPSIS
Retrieves information about PRunSrv on the local machine to start Neo4j programs

.DESCRIPTION
Retrieves information about PRunSrv (Apache Commons Daemon) on the local machine to start Neo4j services and utilities, tailored to the type of Neo4j edition

.PARAMETER Neo4jServer
An object representing a valid Neo4j Server object

.PARAMETER ForServerInstall
Retrieve the PrunSrv command line to install a Neo4j Server

.PARAMETER ForServerUninstall
Retrieve the PrunSrv command line to uninstall a Neo4j Server

.PARAMETER ForServerUpdate
Retrieve the PrunSrv command line to update a Neo4j Server

.PARAMETER ForConsole
Retrieve the PrunSrv command line to start a Neo4j Server in the console.

.OUTPUTS
System.Collections.Hashtable

.NOTES
This function is private to the powershell module

#>
function Get-Neo4jPrunsrv
{
  [CmdletBinding(SupportsShouldProcess = $false,ConfirmImpact = 'Low',DefaultParameterSetName = 'ConsoleInvoke')]
  param(
    [Parameter(Mandatory = $true,ValueFromPipeline = $false)]
    [pscustomobject]$Neo4jServer

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ServerInstallInvoke')]
    [switch]$ForServerInstall

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ServerUninstallInvoke')]
    [switch]$ForServerUninstall

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ServerUpdateInvoke')]
    [switch]$ForServerUpdate

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ServerStartInvoke')]
    [switch]$ForServerStart

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ServerStopInvoke')]
    [switch]$ForServerStop

    ,[Parameter(Mandatory = $true,ValueFromPipeline = $false,ParameterSetName = 'ConsoleInvoke')]
    [switch]$ForConsole
  )

  begin
  {
  }

  process
  {
    $JavaCMD = Get-Java -Neo4jServer $Neo4jServer -ForServer -ErrorAction Stop
    if ($JavaCMD -eq $null)
    {
      Write-Error 'Unable to locate Java'
      return 255
    }

    # JVMDLL is in %JAVA_HOME%\bin\server\jvm.dll
    $JvmDLL = Join-Path -Path (Join-Path -Path (Split-Path $JavaCMD.java -Parent) -ChildPath 'server') -ChildPath 'jvm.dll'
    if (-not (Test-Path -Path $JvmDLL)) { throw "Could not locate JVM.DLL at $JvmDLL" }

    # Get the Service Name
    $Name = Get-Neo4jWindowsServiceName -Neo4jServer $Neo4jServer -ErrorAction Stop

    # Find PRUNSRV for this architecture
    # This check will return the OS architecture even when running a 32bit app on 64bit OS
    switch ((Get-WmiObject -Class Win32_Processor | Select-Object -First 1).Addresswidth) {
      32 { $PrunSrvName = 'prunsrv-i386.exe' } # 4 Bytes = 32bit
      64 { $PrunSrvName = 'prunsrv-amd64.exe' } # 8 Bytes = 64bit
      default { throw "Unable to determine the architecture of this operating system (Integer is $([IntPtr]::Size))" }
    }
    $PrunsrvCMD = Join-Path (Join-Path -Path (Join-Path -Path $Neo4jServer.Home -ChildPath 'bin') -ChildPath 'tools') -ChildPath $PrunSrvName
    if (-not (Test-Path -Path $PrunsrvCMD)) { throw "Could not find PRUNSRV at $PrunsrvCMD" }

    # Build the PRUNSRV command line
    switch ($PsCmdlet.ParameterSetName) {
      "ServerInstallInvoke" {
        $PrunArgs += @("`"//IS//$($Name)`"")
      }
      "ServerUpdateInvoke" {
        $PrunArgs += @("`"//US//$($Name)`"")
      }
      { @("ServerInstallInvoke","ServerUpdateInvoke") -contains $_ } {

        $JvmOptions = @()

        Write-Verbose "Reading JVM settings from configuration"
        # Try neo4j.conf first, but then fallback to neo4j-wrapper.conf for backwards compatibility reasons
        $setting = (Get-Neo4jSetting -ConfigurationFile 'neo4j.conf' -Name 'dbms.jvm.additional' -Neo4jServer $Neo4jServer)
        if ($setting -eq $null) {
          $setting = (Get-Neo4jSetting -ConfigurationFile 'neo4j-wrapper.conf' -Name 'dbms.jvm.additional' -Neo4jServer $Neo4jServer)
        }

        if ($setting -ne $null) {
          # Procrun expects us to split each option with `;` if these characters are used inside the actual option values
          # that will cause problems in parsing. To overcome the problem, we need to escape those characters by placing 
          # them inside single quotes.
          $settingsEscaped = @()
          foreach ($option in $setting.value) {
            $settingsEscaped += $option -replace "([;])",'''$1'''
          }

          $JvmOptions = [array](Merge-Neo4jJavaSettings -Source $JvmOptions -Add $settingsEscaped)
        }

        # Pass through appropriate args from Java invocation to Prunsrv
        # These options take priority over settings in the wrapper
        Write-Verbose "Reading JVM settings from console java invocation"
        $cmdSettings = ($JavaCMD.args | Where-Object { $_ -match '(^-D|^-X)' } | % { $_ -replace "([;])",'''$1''' })
        $JvmOptions = [array](Merge-Neo4jJavaSettings -Source $JvmOptions -Add $cmdSettings)

        $PrunArgs += @("`"--StartMode=jvm`"",
          "`"--StartMethod=start`"",
          "`"--ServiceUser=LocalSystem`"",
          "`"--StartPath=$($Neo4jServer.Home)`"",
          "`"--StartParams=--config-dir=$($Neo4jServer.ConfDir)`"",
          "`"++StartParams=--home-dir=$($Neo4jServer.Home)`"",
          "`"--StopMode=jvm`"",
          "`"--StopMethod=stop`"",
          "`"--StopPath=$($Neo4jServer.Home)`"",
          "`"--Description=Neo4j Graph Database - $($Neo4jServer.Home)`"",
          "`"--DisplayName=Neo4j Graph Database - $Name`"",
          "`"--Jvm=$($JvmDLL)`"",
          "`"--LogPath=$($Neo4jServer.LogDir)`"",
          "`"--StdOutput=$(Join-Path -Path $Neo4jServer.LogDir -ChildPath 'neo4j.log')`"",
          "`"--StdError=$(Join-Path -Path $Neo4jServer.LogDir -ChildPath 'service-error.log')`"",
          "`"--LogPrefix=neo4j-service`"",
          "`"--Classpath=lib/*;plugins/*`"",
          "`"--JvmOptions=$($JvmOptions -join ';')`"",
          "`"--Startup=auto`""
        )

        # Check if Java invocation includes Java memory sizing
        $JavaCMD.args | ForEach-Object -Process {
          if ($Matches -ne $null) { $Matches.Clear() }
          if ($_ -match '^-Xms([\d]+)m$') {
            $PrunArgs += "`"--JvmMs`""
            $PrunArgs += "`"$($matches[1])`""
            Write-Verbose "Use JVM Start Memory of $($matches[1]) MB"
          }
          if ($Matches -ne $null) { $Matches.Clear() }
          if ($_ -match '^-Xmx([\d]+)m$') {
            $PrunArgs += "`"--JvmMx`""
            $PrunArgs += "`"$($matches[1])`""

            Write-Verbose "Use JVM Max Memory of $($matches[1]) MB"
          }
        }

        if ($Neo4jServer.ServerType -eq 'Community') { $serverMainClass = 'org.neo4j.server.CommunityEntryPoint' }
        if ($serverMainClass -eq '') { Write-Error "Unable to determine the Server Main Class from the server information"; return $null }
        $PrunArgs += @("`"--StopClass=$($serverMainClass)`"",
          "`"--StartClass=$($serverMainClass)`"")
      }
      "ServerUninstallInvoke" { $PrunArgs += @("`"//DS//$($Name)`"") }
      "ServerStartInvoke" { $PrunArgs += @("`"//ES//$($Name)`"") }
      "ServerStopInvoke" { $PrunArgs += @("`"//SS//$($Name)`"") }
      "ConsoleInvoke" { $PrunArgs += @("`"//TS//$($Name)`"") }
      default {
        throw "Unknown ParameterSetName $($PsCmdlet.ParameterSetName)"
        return $null
      }
    }

    Write-Output @{ 'cmd' = $PrunsrvCMD; 'args' = $PrunArgs }
  }

  end
  {
  }
}

# SIG # Begin signature block
# MIIQ4QYJKoZIhvcNAQcCoIIQ0jCCEM4CAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQH8w7YFlLCE63JNLG
# KX7zUQIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDNPoijghTwd9Ny
# yoDI00XJExBZU7G5SZgjhKRdMIuC3KCCDcIwggPFMIICraADAgECAgEAMA0GCSqG
# SIb3DQEBCwUAMIGDMQswCQYDVQQGEwJVUzEQMA4GA1UECBMHQXJpem9uYTETMBEG
# A1UEBxMKU2NvdHRzZGFsZTEaMBgGA1UEChMRR29EYWRkeS5jb20sIEluYy4xMTAv
# BgNVBAMTKEdvIERhZGR5IFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5IC0gRzIw
# HhcNMDkwOTAxMDAwMDAwWhcNMzcxMjMxMjM1OTU5WjCBgzELMAkGA1UEBhMCVVMx
# EDAOBgNVBAgTB0FyaXpvbmExEzARBgNVBAcTClNjb3R0c2RhbGUxGjAYBgNVBAoT
# EUdvRGFkZHkuY29tLCBJbmMuMTEwLwYDVQQDEyhHbyBEYWRkeSBSb290IENlcnRp
# ZmljYXRlIEF1dGhvcml0eSAtIEcyMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
# CgKCAQEAv3FiCPH6WTT3G8kYo/eASVjpIoMTpsUgQwE7hPHmhUmfJ+r2hBtOoLTb
# cJjHMgGxBT4HTu70+k8vWTAi56sZVmvigAf88xZ1gDlRe+X5NbZ0TqmNghPktj+p
# A4P6or6KFWp/3gvDthkUBcrqw6gElDtGfDIN8wBmIsiNaW02jBEYt9OyHGC0OPoC
# jM7T3UYH3go+6118yHz7sCtTpJJiaVElBWEaRIGMLKlDliPfrDqBmg4pxRyp6V0e
# tp6eMAo5zvGIgPtLXcwy7IViQyU0AlYnAZG0O3AqP26x6JyIAX2f1PnbU21gnb8s
# 51iruF9G/M7EGwM8CetJMVxpRrPgRwIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/
# MA4GA1UdDwEB/wQEAwIBBjAdBgNVHQ4EFgQUOpqFBxBnKLbv9r0FQW4gwZTaD94w
# DQYJKoZIhvcNAQELBQADggEBAJnbXXnV+ZdZZwNh8X47BjF1LaEgjk9lh7T3ppy8
# 2Okv0Nta7s90jHO0OELaBXv4AnW4/aWx1672194Ty1MQfopG0Zf6ty4rEauQsCeA
# +eifWuk3n6vk32yzhRedPdkkT3mRNdZfBOuAg6uaAi21EPTYkMcEc0DtciWgqZ/s
# nqtoEplXxo8SOgmkvUT9BhU3wZvkMqPtOOjYZPMsfhT8Auqfzf8HaBfbIpA4LXqN
# 0VTxaeNfM8p6PXsK48p/Xznl4nW6xXYYM84s8C9Mrfex585PqMSbSlQGxX991QgP
# 4hz+fhe4rF721BayQwkMTfana7SZhGXKeoji4kS+XPfqHPUwggTQMIIDuKADAgEC
# AgEHMA0GCSqGSIb3DQEBCwUAMIGDMQswCQYDVQQGEwJVUzEQMA4GA1UECBMHQXJp
# em9uYTETMBEGA1UEBxMKU2NvdHRzZGFsZTEaMBgGA1UEChMRR29EYWRkeS5jb20s
# IEluYy4xMTAvBgNVBAMTKEdvIERhZGR5IFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9y
# aXR5IC0gRzIwHhcNMTEwNTAzMDcwMDAwWhcNMzEwNTAzMDcwMDAwWjCBtDELMAkG
# A1UEBhMCVVMxEDAOBgNVBAgTB0FyaXpvbmExEzARBgNVBAcTClNjb3R0c2RhbGUx
# GjAYBgNVBAoTEUdvRGFkZHkuY29tLCBJbmMuMS0wKwYDVQQLEyRodHRwOi8vY2Vy
# dHMuZ29kYWRkeS5jb20vcmVwb3NpdG9yeS8xMzAxBgNVBAMTKkdvIERhZGR5IFNl
# Y3VyZSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgLSBHMjCCASIwDQYJKoZIhvcNAQEB
# BQADggEPADCCAQoCggEBALngyxDUr3a91JNi6zBkuIEIbMME2WIXji//PmXPj85i
# 5jxSHNoWRUtVq3hrY4NikM4PaWyZyBoUi0zMRTPqiNyeo68r/oBhnXlXxM8u9D8w
# PF1H/JoWvMM3lkFRjhFLVPgovtCMvvAwOB7zsCb4Zkdjbd5xJkePOEdT0UYdtOPc
# AOpFrL28cdmqbwDb280wOnlPX0xH+B3vW8LEnWA7sbJDkdikM07qs9YnT60liqXG
# 9NXQpq50BWRXiLVEVdQtKjo++Li96TIKApRkxBY6UPFKrud5M68MIAd/6N8EOcJp
# AmxjUvp3wRvIdIfIuZMYUFQ1S2lOvDvTSS4f3MHSUvsCAwEAAaOCARowggEWMA8G
# A1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgEGMB0GA1UdDgQWBBRAwr0njsw0
# gzCiM9f7bLPwtCyAzjAfBgNVHSMEGDAWgBQ6moUHEGcotu/2vQVBbiDBlNoP3jA0
# BggrBgEFBQcBAQQoMCYwJAYIKwYBBQUHMAGGGGh0dHA6Ly9vY3NwLmdvZGFkZHku
# Y29tLzA1BgNVHR8ELjAsMCqgKKAmhiRodHRwOi8vY3JsLmdvZGFkZHkuY29tL2dk
# cm9vdC1nMi5jcmwwRgYDVR0gBD8wPTA7BgRVHSAAMDMwMQYIKwYBBQUHAgEWJWh0
# dHBzOi8vY2VydHMuZ29kYWRkeS5jb20vcmVwb3NpdG9yeS8wDQYJKoZIhvcNAQEL
# BQADggEBAAh+bJMQyDi4lqmQS/+hX08E72w+nIgGyVCPpnP3VzEbvrzkL9v4utNb
# 4LTn5nliDgyi12pjczG19ahIpDsILaJdkNe0fCVPEVYwxLZEnXssneVe5u8MYaq/
# 5Cob7oSeuIN9wUPORKcTcA2RH/TIE62DYNnYcqhzJB61rCIOyheJYlhEG6uJJQEA
# D83EG2LbUbTTD1Eqm/S8c/x2zjakzdnYLOqum/UqspDRTXUYij+KQZAjfVtL/qQD
# WJtGssNgYIP4fVBBzsKhkMO77wIv0hVU7kQV2Qqup4oz7bEtdjYm3ATrn/dhHxXc
# h2/uRpYoraEmfQoJpy4Eo428+LwEMAEwggUhMIIECaADAgECAgkAhHYYKGL3whow
# DQYJKoZIhvcNAQELBQAwgbQxCzAJBgNVBAYTAlVTMRAwDgYDVQQIEwdBcml6b25h
# MRMwEQYDVQQHEwpTY290dHNkYWxlMRowGAYDVQQKExFHb0RhZGR5LmNvbSwgSW5j
# LjEtMCsGA1UECxMkaHR0cDovL2NlcnRzLmdvZGFkZHkuY29tL3JlcG9zaXRvcnkv
# MTMwMQYDVQQDEypHbyBEYWRkeSBTZWN1cmUgQ2VydGlmaWNhdGUgQXV0aG9yaXR5
# IC0gRzIwHhcNMTcxMTA3MTkzNzAzWhcNMjAxMTA3MTkzNzAzWjBiMQswCQYDVQQG
# EwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTESMBAGA1UEBxMJU2FuIE1hdGVvMRQw
# EgYDVQQKEwtOZW80aiwgSW5jLjEUMBIGA1UEAxMLTmVvNGosIEluYy4wggEiMA0G
# CSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDSoPiG1pU1Lvqo+aZsFTrUwaV1sDWV
# BtfWzSnDKB3bUJeC7DhekXtt1FORi3PB4YAC/CSMGgwoBHuqgGuRaJbHjRlmYaZZ
# dKVsgvmDwfEvv16jzoyUR8TMTTjCemIDAHwArEadkffpsgnFpQ6KG6+gag/39FXy
# M2rGmFaqSGkqjVRNu4zN5GQu8+CUvRuZO2zEuKdA4wv9ZlmWbV3bpCGIN3Zl4p39
# Fatz3KYNi4g8lFXhB8tJfBToRuqxLZpcuyrXG3PeLa6DNoYOJ3j49DJOEw8Wj9cn
# qvAaI3CNE2klZ7RScE47YUh7rVpl/ykp9ohgZDtvhAA5RYI5KCnc+oXHAgMBAAGj
# ggGFMIIBgTAMBgNVHRMBAf8EAjAAMBMGA1UdJQQMMAoGCCsGAQUFBwMDMA4GA1Ud
# DwEB/wQEAwIHgDA1BgNVHR8ELjAsMCqgKKAmhiRodHRwOi8vY3JsLmdvZGFkZHku
# Y29tL2dkaWcyczUtMy5jcmwwXQYDVR0gBFYwVDBIBgtghkgBhv1tAQcXAjA5MDcG
# CCsGAQUFBwIBFitodHRwOi8vY2VydGlmaWNhdGVzLmdvZGFkZHkuY29tL3JlcG9z
# aXRvcnkvMAgGBmeBDAEEATB2BggrBgEFBQcBAQRqMGgwJAYIKwYBBQUHMAGGGGh0
# dHA6Ly9vY3NwLmdvZGFkZHkuY29tLzBABggrBgEFBQcwAoY0aHR0cDovL2NlcnRp
# ZmljYXRlcy5nb2RhZGR5LmNvbS9yZXBvc2l0b3J5L2dkaWcyLmNydDAfBgNVHSME
# GDAWgBRAwr0njsw0gzCiM9f7bLPwtCyAzjAdBgNVHQ4EFgQUvj4gytCNJMDPx3lW
# v0klX6YK41IwDQYJKoZIhvcNAQELBQADggEBABzaEnMJczETlZUdZE36x84eQS2A
# mumczZzTMbZ4IhJwxF8vVz2+Q+0BcR5uwAXa+s167yqIZsxAub3nu8GzYAF7D7wH
# DC1H1JNkgfnZf1w2WWGL6jkbr5RGrLlU2xE8o03iuFglU4QQl9ouXXBLAsLo/q+p
# MrPs+EO+g3DwXGFtjAKzkrMzJD5Ia2kVSC2aAXrffwRqMpbKVxkf0TQadMGLa6dV
# ybYH7qBfDZ+u8P2KY0qQyQYY63WoVk7TIq1VkbmRXtcvm3/plWPUNTPPEy0Dfnjn
# dA2UByib6/iqdnSZ7MYit31rmSsRAS3Wil/qqOGlVfYrSm2s64ryPMOacAkxggJ1
# MIICcQIBATCBwjCBtDELMAkGA1UEBhMCVVMxEDAOBgNVBAgTB0FyaXpvbmExEzAR
# BgNVBAcTClNjb3R0c2RhbGUxGjAYBgNVBAoTEUdvRGFkZHkuY29tLCBJbmMuMS0w
# KwYDVQQLEyRodHRwOi8vY2VydHMuZ29kYWRkeS5jb20vcmVwb3NpdG9yeS8xMzAx
# BgNVBAMTKkdvIERhZGR5IFNlY3VyZSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgLSBH
# MgIJAIR2GChi98IaMA0GCWCGSAFlAwQCAQUAoIGEMBgGCisGAQQBgjcCAQwxCjAI
# oAKAAKECgAAwGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQwHAYKKwYBBAGCNwIB
# CzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkEMSIEIIpDqqBIIV+zflSbwaEf
# RLZaoFEPxML2k4HlfcE2Z+OuMA0GCSqGSIb3DQEBAQUABIIBAEIct7D7uxUKnqxD
# T4dZHXqkxjiunz1ijraCtXUjLVVQTFEpeHuMpTZsvYVV5P/fD3o/ZZqLzfA7lMmS
# Xo4Pn1E2uLKpygN80h6WdadzvPnJzguSBwF5cA+DOQ8+IUu6Qz5LJSFve5An1or6
# qwK5b6U5NP6YA8dN193VoI9funytwaaRr8Yamk/xiGrtLU3oMmk447Ac3orsnE2M
# ujQR2uPIRVRYyxDozyEfvUFBCiN64vCN4b9XPD/Oiq5oiiHZ9cG6XutGsTs2cxyW
# 8pMsSLy3mwGj4YFwHOiyK7+5X48j2XGckUUKxaGGk87qJ6F/JdAgYjt5+9DmKAzc
# Ip5wtQw=
# SIG # End signature block
