import laspy
import numpy as np
import rasterio
from rasterio.transform import from_origin

def las_to_tif(input_las_path, output_tif_path, resolution=1.0):
    # Abrir o arquivo LAS
    las = laspy.read(input_las_path)
    
    # Extrair coordenadas X, Y, Z
    x = las.x
    y = las.y
    z = las.z
    
    # Calcular limites do grid
    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    
    # Calcular dimensões do raster
    width = int((x_max - x_min) / resolution) + 1
    height = int((y_max - y_min) / resolution) + 1
    
    # Criar grid vazio
    grid = np.full((height, width), np.nan)
    
    # Converter coordenadas para índices do grid
    x_idx = ((x - x_min) / resolution).astype(int)
    y_idx = ((y_max - y) / resolution).astype(int)  # Inverter Y para orientação correta
    
    # Preencher o grid com valores Z
    for xi, yi, zi in zip(x_idx, y_idx, z):
        if 0 <= xi < width and 0 <= yi < height:
            grid[yi, xi] = zi
    
    # Criar transformação geográfica
    transform = from_origin(x_min, y_max, resolution, resolution)
    
    # Configuração do arquivo TIFF
    profile = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': rasterio.float32,
        'crs': None,  # Se o LAS tiver CRS, você pode especificá-lo aqui
        'transform': transform,
        'nodata': np.nan
    }
    
    # Escrever o arquivo TIFF
    with rasterio.open(output_tif_path, 'w', **profile) as dst:
        dst.write(grid.astype(rasterio.float32), 1)

    print(f"Conversão concluída: {output_tif_path}")

# Exemplo de uso
if __name__ == "__main__":
    input_file = "/Users/andersonstolfi/Documents/coding/lidar-processing/app/files/las/nuvem_processada.las"
    output_file = "/Users/andersonstolfi/Documents/coding/lidar-processing/app/files/tif/nuvem_matriz.tif"
    las_to_tif(input_file, output_file, resolution=1.0)