from src.part3.analytics_lambda import run

def lambda_handler(event, context):
    run()
    return {"status": "lambda analytics complete"}
