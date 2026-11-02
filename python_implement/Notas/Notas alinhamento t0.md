Limitar a cadência não resolve nenhum dos três efeitos. O offset de 3 cm é calibração. O atraso de 0,08 s é de tempo, não de frequência. O arranque tardio do ZED é dado em falta. Duas coisas a pesar antes de o decidires no outro chat:

A janela de 0,5 s do _calcular_vel e do _calcular_acel mede tempo, não número de amostras, por isso a velocidade e a aceleração já saem comparáveis entre 98 e 60 linhas/s.
Limitar o LiDAR a 60 Hz descarta dados que já tens. Para comparar os dois sensores (ICC, Bland-Altman) dá igual interpolar o LiDAR nos instantes do ZED na análise, como fiz acima com np.interp, e guardar os CSVs com a cadência original.

Para levares ao outro chat, são estes os três factos: offset de −2,8 cm em repouso, atraso do ZED entre 0,06 e 0,10 s, e 1,88 s sem linhas do ZED no arranque.