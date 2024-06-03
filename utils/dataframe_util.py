import pandas as pd

def get_max_and_mean_csv(csv_file_path, column_name):
    df = pd.read_csv(csv_file_path)
    if column_name not in df.columns:
        raise ValueError("Non-existent column")
    max_value = df[column_name].max()
    average_value = df[column_name].mean()
    return max_value, average_value

def calculate_congestion(prediction, average_sales, max_sales, average_congestion=40):
    if prediction <= 0:
        return [0]
    elif prediction == average_sales:
        return [average_congestion]
    else:
        if prediction >= max_sales:
            return [100]
        else:
            return average_congestion + ((prediction - average_sales) / (max_sales - average_sales)) * (100 - average_congestion)
