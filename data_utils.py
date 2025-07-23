import pandas as pd
import io

def load_csv(file_path):
    """
    Загрузить CSV файл в pandas DataFrame.
    Возвращает DataFrame при успехе, вызывает исключение при ошибке.
    """
    df = pd.read_csv(file_path)
    return df

def get_info_string(df):
    """
    Возвращает строку с информацией о DataFrame (структура) и первыми несколькими строками.
    """
    buf = io.StringIO()
    df.info(buf=buf)  # записать вывод df.info() в буфер
    info_str = buf.getvalue()
    head_str = df.head().to_string()
    info_and_head = f"{info_str}\n\nHead of data:\n{head_str}"
    return info_and_head

def filter_data(df, selected_cuts, selected_colors, selected_clarities,
                carat_min, carat_max, use_carat,
                price_min, price_max, use_price):
    """
    Отфильтровать DataFrame на основе выбранных категориальных значений и числовых диапазонов.
    Возвращает новый DataFrame с отфильтрованными результатами.
    """
    mask = pd.Series(True, index=df.index)
    # Применить категориальные фильтры
    if selected_cuts:
        mask &= df['cut'].isin(selected_cuts)
    if selected_colors:
        mask &= df['color'].isin(selected_colors)
    if selected_clarities:
        mask &= df['clarity'].isin(selected_clarities)
    # Применить числовые диапазонные фильтры
    if use_carat and carat_min is not None and carat_max is not None:
        mask &= (df['carat'] >= float(carat_min)) & (df['carat'] <= float(carat_max))
    if use_price and price_min is not None and price_max is not None:
        mask &= (df['price'] >= float(price_min)) & (df['price'] <= float(price_max))
    return df[mask].copy()



def get_recommendations(df):
    if df is None or df.empty:
        return [("Нет данных", "")]

    rows = []

    # Вес
    corr_carat = df[['carat', 'price']].corr().iloc[0, 1]
    rows.append((
        "Вес алмаза (carat)",
        f"Корреляция с ценой ≈ {corr_carat:.3f}"
    ))

    # Огранка: самая дорогая и самая массовая
    cut_stats = df.groupby('cut')['price'].agg(['mean', 'size'])
    high_cut, high_val = cut_stats['mean'].idxmax(), cut_stats['mean'].max()
    common_cut = cut_stats['size'].idxmax()
    common_val = cut_stats.loc[common_cut, 'mean']
    rows.append((
        "Огранка (cut)",
        f"{high_cut} vs {common_cut} avg: "
        f"{int(high_val):,} vs {int(common_val):,}"
    ))

    # Цвет: топ‑3 по доле
    color_share = (df['color'].value_counts(normalize=True) * 100).round(2)
    top_colors = ", ".join(
        [f"{c} ({v:.2f}%)" for c, v in color_share.head(3).items()])
    rows.append(("Цвет (color)", top_colors))

    # Чистота: топ‑3 по доле
    clar_share = (df['clarity'].value_counts(normalize=True) * 100).round(0)
    top_clar = ", ".join(
        [f"{c} ({int(v)}%)" for c, v in clar_share.head(3).items()])
    rows.append(("Чистота (clarity)", top_clar))

    # Диапазон цен (IQR + медиана)
    q25, q75 = df['price'].quantile([.25, .75])
    median = df['price'].median()
    rows.append((
        "Диапазон цен",
        f"{int(q25):,}–{int(q75):,} USD (медиана {int(median):,})"
    ))

    return rows






