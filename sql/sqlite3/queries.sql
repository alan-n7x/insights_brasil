SELECT
    e.nome AS ibge_estado,
    SUM(im.valor) AS total
FROM ibge_indicadormunicipio im
JOIN ibge_municipio m
    ON m.id = im.municipio_id
JOIN ibge_estado e
    ON e.id = m.estado_id
JOIN ibge_indicador i
    ON i.id = im.indicador_id
WHERE
    i.codigo = 'POPULACAO'
    AND im.ano = 2021
GROUP BY
    e.nome
ORDER BY
    total DESC;