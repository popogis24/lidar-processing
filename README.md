
# Metodologia para Processamento de Dados LiDAR de Vegetação

## 1. Etapa: Leitura e Filtragem dos Dados LiDAR (.las)

1. **Importação das Bibliotecas Necessárias:**

   ```python
   import laspy
   import numpy as np
   from osgeo import gdal, osr
   ```
2. **Leitura do Arquivo .las:**

   ```python
   in_las = laspy.read("seu_arquivo.las")
   ```
3. **Filtragem dos Pontos do Solo:**

   * Utilize a classificação dos pontos LiDAR (atributo `classification`) para identificar os pontos do solo (geralmente classificados como 2).
   * Crie máscaras booleanas para separar os pontos do solo e os pontos de vegetação/estruturas.

   ```python
   solo_mask = in_las.classification == 2
   solo_pontos = in_las.points[solo_mask]
   vegetacao_mask = in_las.classification != 2
   vegetacao_pontos = in_las.points[vegetacao_mask]
   ```

## 2. Etapa: Geração do Modelo Digital do Terreno (MDT)

1. **Criação da Grade Regular:**

   * Determine a extensão espacial da área de interesse a partir dos pontos do solo.
   * Defina a resolução desejada para o MDT (tamanho do pixel).
   * Crie uma grade regular (matriz) com as dimensões e resolução definidas.

   ```python
   x_min, x_max = solo_pontos.x.min(), solo_pontos.x.max()
   y_min, y_max = solo_pontos.y.min(), solo_pontos.y.max()
   resolucao = 1.0  # Resolução em metros
   largura = int((x_max - x_min) / resolucao)
   altura = int((y_max - y_min) / resolucao)
   mdt = np.zeros((altura, largura))
   ```
2. **Interpolação dos Pontos do Solo:**

   * Utilize um algoritmo de interpolação (e.g., média, IDW, krigagem) para estimar a altitude do terreno em cada célula da grade.
   * Atribua os valores de altitude interpolados à matriz do MDT.

   ```python
   # Exemplo simples de interpolação por média
   for i in range(altura):
       for j in range(largura):
           x = x_min + j * resolucao
           y = y_max - i * resolucao
           pontos_proximos = solo_pontos[
               (solo_pontos.x >= x - resolucao / 2) &
               (solo_pontos.x < x + resolucao / 2) &
               (solo_pontos.y >= y - resolucao / 2) &
               (solo_pontos.y < y + resolucao / 2)
           ]
           if len(pontos_proximos) > 0:
               mdt[i, j] = np.mean(pontos_proximos.z)
   ```
3. **Exportação do MDT para .tif:**

   * Utilize a biblioteca GDAL para criar um arquivo .tif a partir da matriz do MDT.
   * Defina o sistema de coordenadas de referência (CRS) do arquivo .tif.

   ```python
   driver = gdal.GetDriverByName("GTiff")
   mdt_tif = driver.Create("mdt.tif", largura, altura, 1, gdal.GDT_Float32)
   mdt_tif.SetGeoTransform((x_min, resolucao, 0, y_max, 0, -resolucao))
   srs = osr.SpatialReference()
   srs.ImportFromEPSG(32723)  # Substitua pelo seu EPSG
   mdt_tif.SetProjection(srs.ExportToWkt())
   mdt_tif.GetRasterBand(1).WriteArray(mdt)
   mdt_tif = None
   ```

## 3. Etapa: Geração do Modelo de Estruturas Acima do Solo

1. **Criação da Grade Regular:**

   * Repita o processo de criação da grade regular, mas utilizando os pontos de vegetação/estruturas.

   ```python
   x_min, x_max = vegetacao_pontos.x.min(), vegetacao_pontos.x.max()
   y_min, y_max = vegetacao_pontos.y.min(), vegetacao_pontos.y.max()
   largura = int((x_max - x_min) / resolucao)
   altura = int((y_max - y_min) / resolucao)
   estruturas = np.zeros((altura, largura))
   ```
2. **Interpolação dos Pontos de Vegetação/Estruturas:**

   * Repita o processo de interpolação, mas utilizando os pontos de vegetação/estruturas.

   ```python
   # Exemplo simples de interpolação por média
   for i in range(altura):
       for j in range(largura):
           x = x_min + j * resolucao
           y = y_max - i * resolucao
           pontos_proximos = vegetacao_pontos[
               (vegetacao_pontos.x >= x - resolucao / 2) &
               (vegetacao_pontos.x < x + resolucao / 2) &
               (vegetacao_pontos.y >= y - resolucao / 2) &
               (vegetacao_pontos.y < y + resolucao / 2)
           ]
           if len(pontos_proximos) > 0:
               estruturas[i, j] = np.mean(pontos_proximos.z)
   ```
3. **Exportação do Modelo de Estruturas para .tif:**

   * Repita o processo de exportação para .tif.

   ```python
   driver = gdal.GetDriverByName("GTiff")
   estruturas_tif = driver.Create("estruturas.tif", largura, altura, 1, gdal.GDT_Float32)
   estruturas_tif.SetGeoTransform((x_min, resolucao, 0, y_max, 0, -resolucao))
   srs = osr.SpatialReference()
   srs.ImportFromEPSG(32723)  # Substitua pelo seu EPSG
   estruturas_tif.SetProjection(srs.ExportToWkt())
   estruturas_tif.GetRasterBand(1).WriteArray(estruturas)
   estruturas_tif = None
   ```

## Observações

* A escolha do algoritmo de interpolação pode impactar significativamente a qualidade dos resultados.
* A resolução do MDT e do modelo de estruturas deve ser definida de acordo com a densidade dos pontos LiDAR e a precisão desejada.
* O sistema de coordenadas de referência (CRS) deve ser o mesmo para ambos os arquivos .tif.
* Este guia fornece uma base para o processamento dos dados LiDAR. Adaptações podem ser necessárias dependendo das características específicas dos seus dados e dos objetivos do projeto.
