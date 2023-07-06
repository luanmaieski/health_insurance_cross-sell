import pickle
import numpy as np
import pandas as pd

class HealthInsurance( object ):
    def __init__( self ):
        self.home_path = '/Users/Luan/repos/health_insurance_cross-sell/'
        self.annual_premium_scaler = pickle.load( open( self.home_path + 'features/annual_premium_scaler.pkl', 'rb'))
        self.age_scaler = pickle.load( open( self.home_path + 'features/age_scaler.pkl', 'rb'))
        self.vintage_scaler = pickle.load( open( self.home_path + 'features/vintage_scaler.pkl', 'rb'))
        self.target_encode_gender_scaler = pickle.load( open( self.home_path + 'features/target_encode_gender_scaler.pkl','rb'))
        self.target_encode_region_code_scaler = pickle.load( open( self.home_path + 'features/target_encode_region_code_scaler.pkl', 'rb'))
        self.fe_policy_sales_channel_scaler = pickle.load( open( self.home_path + 'features/fe_policy_sales_channel_scaler.pkl', 'rb'))
        
    def data_cleaning( self, df1 ):
        # Rename Columns
        df1.columns = df1.columns.str.lower()
        
        return df1
    
    def feature_engineering( self, df2 ):
        # vehicle age
        df2['vehicle_age'] = df2['vehicle_age'].apply( lambda x: 'over_2_years' if x=='> 2 Years' else 'between_1_2_year' if x=='1-2 Year' else 'below_1_year' ) 

        # vehicle damage
        df2['vehicle_damage'] = df2['vehicle_damage'].apply( lambda x: 1 if x=='Yes' else 0 )
        
        return df2
    
    def data_preparation( self, df5 ):
        # annaul_premium
        df5['annual_premium'] = self.annual_premium_scaler.transform( df5[['annual_premium']].values )
        
        # age
        df5['age'] = self.age_scaler.transform( df5[['age']].values )

        # vintage
        df5['vintage'] = self.vintage_scaler.transform( df5[['vintage']].values )

        ## Encoder

        # gender - One Hot Encoding ou Target Encoding
        df5.loc[:, 'gender'] = df5['gender'].map( self.target_encode_gender_scaler )
        
        # region_code - Target Encoding
        df5.loc[:, 'region_code'] = df5['region_code'].map( self.target_encode_region_code_scaler )

        # vehicle_age - Ordinal Encoding
        vehicle_age_dict = {'below_1_year': 0 , 'between_1_2_year': 1, 'over_2_years': 2}
        df5['vehicle_age'] = df5['vehicle_age'].map( vehicle_age_dict )

        # policy_sales_channel - Target Encoding ou Frequency Encoding
        df5.loc[:, 'policy_sales_channel'] = df5['policy_sales_channel'].map( self.fe_policy_sales_channel_scaler )


        # 6.0. Feature Selection
        cols_selected = ['vintage', 'annual_premium', 'age', 'region_code', 'vehicle_damage', 'policy_sales_channel',                              'previously_insured']
        
        return df5[ cols_selected ]
    
    def get_prediction( self, model, original_data, test_data ):
        # model prediction
        pred = model.predict_proba( test_data )
        
        # join prediction into original data
        original_data['score'] = pred[:, 1].tolist()
        original_data = original_data.sort_values('score', ascending=False)
        
        return original_data.to_json( orient='records', date_format='iso')