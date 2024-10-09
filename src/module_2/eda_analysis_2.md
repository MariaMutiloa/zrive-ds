```python
Calidad de los datos:
Los datos del dataset están en buen estado, sin valores nulos ni duplicados.
```


```python
Dataset Box Builder:
Tamaño del Dataset:El dataset contiene 2,880,549 registros y 27 columnas.

Datos de Productos y Compras:
    Productos: Cada registro está asociado a un variant_id, representando una variante de un producto. Las variantes están categorizadas por product_type (como "ricepastapulses").
    Usuarios: Las compras están asociadas a un user_id, lo que permite identificar la actividad de compra de cada usuario. También se tiene la columna user_order_seq, que indica la secuencia de pedidos de cada usuario.
    Secuencia de Pedidos: La columna user_order_seq indica el número de veces que un usuario ha realizado un pedido. 

Tipos de Datos:
    Las columnas incluyen identificadores (variant_id, order_id, user_id), fechas (created_at, order_date), variables numéricas (normalised_price, discount_pct, global_popularity), y booleanas (outcome, ordered_before, abandoned_before, etc.).
    Outcome (Comprado/No Comprado): La columna outcome es fundamental, pues indica si el producto fue comprado (outcome = 1) o no (outcome = 0), permitiendo análisis sobre comportamiento de compra.
```


```python
Análisis general:
Se observa claramente que la gran mayoría de los productos en el conjunto de datos no fueron comprados (outcome = 0). La barra que representa los "no comprados" (0) es mucho más alta, mientras que la barra de "comprados" (1) es muy pequeña.
Esto indica un desequilibrio significativo en el conjunto de datos, lo que significa que en la mayoría de los casos, los productos no se compraron.
La distribución está fuertemente sesgada hacia la izquierda, con la gran mayoría de los precios normalizados concentrándose en el rango bajo, especialmente entre 0 y 0.3.
Esto sugiere que la mayoría de los productos en el conjunto de datos tienen precios relativamente bajos. Dado que se trata de precios normalizados, esto podría reflejar una tendencia de la plataforma de vender productos más económicos.
No hay una diferencia clara en la distribución de precios normalizados entre los grupos que compraron y los que no:
    Media similar: Tanto el grupo que compró como el que no compraron presentan una media de precio normalizado similar. Esto sugiere que, en promedio, el precio no parece ser un factor determinante para la decisión de compra.
    Rango similar: La caja de ambos grupos tiene un tamaño similar, lo que indica que la dispersión de los precios normalizados es comparable entre ambos grupos.
Presencia de outliers:
    En ambos grupos se observan outliers (puntos individuales fuera de los bigotes). Estos outliers podrían corresponder a productos con precios extremadamente altos o bajos, o a situaciones especiales que no siguen el patrón general.

El descuento no es un factor determinante: Basándonos en este análisis, parece que ofrecer un descuento más alto no garantiza necesariamente que un cliente realice una compra.

Los clientes repetidores compran más: La barra correspondiente a los clientes que han comprado previamente (ordered_before = 1) y que volvieron a comprar (Outcome = 1) es significativamente más alta que las otras barras. Esto indica que los clientes que ya han realizado una compra tienen una mayor probabilidad de realizar compras futuras.
Los clientes nuevos tienen una tasa de conversión más baja: La barra correspondiente a los clientes nuevos (ordered_before = 0) que realizaron una compra (Outcome = 1) es mucho más baja. Esto sugiere que la tasa de conversión de los clientes nuevos es menor comparada con la de los clientes repetidores.
Esto indica la importancia de la retención de clientes. Los clientes existentes son más valiosos para la empresa, ya que tienen una mayor probabilidad de realizar compras repetidas.Por ende, Es fundamental implementar estrategias para fomentar la lealtad de los clientes y convertirlos en clientes recurrentes.
```
