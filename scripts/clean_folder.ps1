$dir = "c:\AGY\BAROMETRO\documentos_barometros_regionales"
$files = Get-ChildItem -Path $dir -File

foreach ($f in $files) {
    $name = $f.Name
    # Keep only files explicitly belonging to 2024 results or 2024 comparison
    if ($name -like "*Informe-Nacional-Barometro-2024*" -or 
        $name -like "*Resultados-2019-2022-2024-Los-Lagos.pdf*" -or 
        $name -like "*barometro-regional-octubre-2025.pdf*" -or 
        $name -like "*251124-Cuestionario-Estudio-Barometro-Regional-Los-Lagos.pdf*") {
        Write-Host "CONSERVANDO: $name"
    } else {
        Write-Host "ELIMINANDO: $name"
        Remove-Item -Path $f.FullName -Force
    }
}

Write-Host "`nArchivos 2024 finales conservados en $dir :"
Get-ChildItem -Path $dir | Select-Object Name, @{Name="MB"; Expression={[math]::round($_.Length / 1MB, 2)}}
