class KALPGenieAdapter:
    name='KALP Genie Creative Engine Adapter'
    contract_version='0.1'
    def wrap(self, ad_package):
        return {'module':'KALP AdManthan','parent':'KALP Genie Creative Engine','handoff_type':'CREATIVE_PRODUCTION_PACKAGE','payload':ad_package}
