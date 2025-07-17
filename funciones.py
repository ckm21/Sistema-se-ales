def detectar_senales(df):
    df["Martillo"] = False
    df["Estrella Fugaz"] = False
    df["Doji"] = False
    df["Envolvente Alcista"] = False
    df["Envolvente Bajista"] = False

    for i in range(1, len(df)):
        o, h, l, c = df.iloc[i][["open", "high", "low", "close"]]
        prev_o, prev_c = df.iloc[i-1][["open", "close"]]

        cuerpo = abs(c - o)
        mecha_superior = h - max(c, o)
        mecha_inferior = min(c, o) - l

        if cuerpo < mecha_inferior * 0.2 and mecha_superior < cuerpo:
            df.at[df.index[i], "Martillo"] = True

        if cuerpo < mecha_superior * 0.2 and mecha_inferior < cuerpo:
            df.at[df.index[i], "Estrella Fugaz"] = True

        if cuerpo <= (h - l) * 0.1:
            df.at[df.index[i], "Doji"] = True

        if prev_c < prev_o and c > o and c > prev_o:
            df.at[df.index[i], "Envolvente Alcista"] = True

        if prev_c > prev_o and c < o and c < prev_o:
            df.at[df.index[i], "Envolvente Bajista"] = True

    return df

def detectar_tendencia(df, ventana=10):
    df["Media_Movil"] = df["close"].rolling(window=ventana).mean()
    df["Tendencia"] = "Lateral"

    for i in range(ventana, len(df)):
        actual = df["Media_Movil"].iloc[i]
        previo = df["Media_Movil"].iloc[i - 1]

        if actual > previo:
            df.at[df.index[i], "Tendencia"] = "Alcista"
        elif actual < previo:
            df.at[df.index[i], "Tendencia"] = "Bajista"
        else:
            df.at[df.index[i], "Tendencia"] = "Lateral"

    return df
