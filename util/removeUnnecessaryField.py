import pandas as pd


routes_path = "../raw_data/routes.txt"
routes_data = pd.read_csv(routes_path)
routes_data = routes_data.drop('agency_id', axis=1)

routes_data.to_csv('../resources/routes.csv', index=False)