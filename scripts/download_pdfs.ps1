$outputDir = "c:\AGY\BAROMETRO\documentos_barometros_regionales"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Directorio de destino: $outputDir"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

$sites = @(
    "https://ceder.ulagos.cl/barometro-regional-2/",
    "https://www.politicaspublicasdelnorte.cl/",
    "https://www.politicaspublicasdelnorte.cl/estudios/",
    "https://www.centroestudiosnuble.cl/",
    "http://www.auregionales.cl/",
    "https://crea-sur.cl/"
)

$pdfUrls = @{}

function Extract-PdfLinks($targetUrl) {
    try {
        Write-Host "Scrapeando $targetUrl ..."
        $req = [System.Net.WebRequest]::Create($targetUrl)
        $req.UserAgent = $headers['User-Agent']
        $req.Timeout = 10000
        $res = $req.GetResponse()
        $stream = $res.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $html = $reader.ReadToEnd()
        $reader.Close()
        $res.Close()

        $matches = [regex]::Matches($html, 'href=["'']([^"'']+\.pdf.*?)["'']', 'IgnoreCase')
        foreach ($m in $matches) {
            $link = $m.Groups[1].Value
            if ($link -notlike "http*") {
                $base = [Uri]$targetUrl
                $link = (New-Object Uri($base, $link)).AbsoluteUri
            }
            if ($link -like "*barometro*" -or $link -like "*informe*" -or $link -like "*boletin*" -or $link -like "*resultado*" -or $link -like "*2024*" -or $link -like "*2022*" -or $link -like "*2023*" -or $link -like "*2025*" -or $targetUrl -like "*barometro*") {
                $pdfUrls[$link] = $targetUrl
            }
        }
    } catch {
        Write-Host "Error en $targetUrl : $_"
    }
}

foreach ($site in $sites) {
    Extract-PdfLinks -targetUrl $site
}

$ddgQueries = @(
    "filetype:pdf Barómetro Regional 2024 site:ulagos.cl",
    "filetype:pdf Barómetro Regional 2024 site:politicaspublicasdelnorte.cl",
    "filetype:pdf Barómetro Regional 2024 site:udec.cl",
    "filetype:pdf Barómetro Regional 2024 site:centroestudiosnuble.cl",
    "filetype:pdf Barómetro Regional 2024 site:auregionales.cl",
    "filetype:pdf Barometro Regional Antofagasta 2024",
    "filetype:pdf Barometro Regional Biobio 2024",
    "filetype:pdf Barometro Regional Los Lagos 2024",
    "filetype:pdf Barometro Regional Nuble 2024"
)

Add-Type -AssemblyName System.Web

foreach ($q in $ddgQueries) {
    try {
        $encodedQ = [System.Web.HttpUtility]::UrlEncode($q)
        $ddgUrl = "https://html.duckduckgo.com/html/?q=$encodedQ"
        Write-Host "Buscando en DDG: $q"
        $req = [System.Net.WebRequest]::Create($ddgUrl)
        $req.UserAgent = $headers['User-Agent']
        $req.Timeout = 10000
        $res = $req.GetResponse()
        $stream = $res.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $html = $reader.ReadToEnd()
        $reader.Close()
        $res.Close()

        $matches = [regex]::Matches($html, 'href=["'']([^"'']+\.pdf.*?)["'']', 'IgnoreCase')
        foreach ($m in $matches) {
            $link = $m.Groups[1].Value
            if ($link -like "*uddg=*") {
                $parts = $link -split "uddg="
                if ($parts.Length -gt 1) {
                    $cleanLink = [System.Web.HttpUtility]::UrlDecode(($parts[1] -split "&")[0])
                    if ($cleanLink -like "*.pdf*") {
                        $pdfUrls[$cleanLink] = "DDG Search"
                    }
                }
            } elseif ($link -like "*.pdf*") {
                $pdfUrls[$link] = "DDG Search"
            }
        }
    } catch {
        Write-Host "Error buscando DDG: $_"
    }
}

Write-Host "`nURLs de PDF encontradas: $($pdfUrls.Count)"

$count = 0
foreach ($url in $pdfUrls.Keys) {
    try {
        $count++
        $uri = [Uri]$url
        $filename = [System.IO.Path]::GetFileName($uri.AbsolutePath)
        if ([string]::IsNullOrWhiteSpace($filename) -or $filename -notlike "*.pdf*") {
            $filename = "barometro_doc_$count.pdf"
        } else {
            $filename = ($filename -split "\?")[0]
            if ($filename -notlike "*.pdf") {
                $filename = "$filename.pdf"
            }
            $filename = "barometro_$filename"
        }
        
        $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
        foreach ($c in $invalidChars) {
            $filename = $filename.Replace($c, '_')
        }

        $destPath = Join-Path $outputDir $filename
        Write-Host "[$count/$($pdfUrls.Count)] Descargando: $url -> $destPath"
        
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", $headers['User-Agent'])
        $wc.DownloadFile($url, $destPath)
        
        $fileInfo = Get-Item $destPath
        Write-Host "  -> Guardado exitosamente ($($fileInfo.Length) bytes)"
    } catch {
        Write-Host "  -> Error descargando $url : $_"
    }
}

Write-Host "`nProceso completado. Revisa la carpeta: $outputDir"
