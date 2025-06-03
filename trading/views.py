from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import threading
import time
import importlib

# Global state tracking
bot_state = {
    "is_running": False,
    "last_run": None,
    "last_result": None
}

@csrf_exempt
def trigger_bot(request):
    """Endpoint to execute trading_logic.py exactly as-is"""
    if request.GET.get('token') != os.getenv('UPTIMEROBOT_TOKEN'):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if bot_state["is_running"]:
        return JsonResponse({
            "status": "already_running",
            "last_run": bot_state["last_run"]
        })
    
    def run_script():
        global bot_state
        bot_state["is_running"] = True
        start_time = time.time()
        
        try:
            # Dynamically import your unmodified script
            trading_module = importlib.import_module('trading.trading_logic')
            
            # Check if script has if __name__ == "__main__" block
            if hasattr(trading_module, '__main__'):
                # Run the script exactly as it would run standalone
                trading_module.__main__()
                result = {"status": "completed"}
            else:
                # For scripts without main block
                result = {"status": "completed_no_main"}
            
        except Exception as e:
            result = {
                "status": "error",
                "error": str(e)
            }
        finally:
            bot_state["is_running"] = False
            bot_state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            bot_state["last_result"] = {
                **result,
                "execution_time": round(time.time() - start_time, 2)
            }
    
    # Start execution thread
    thread = threading.Thread(target=run_script)
    thread.daemon = True  # Allows thread to exit if main process ends
    thread.start()
    
    return JsonResponse({
        "status": "started",
        "message": "Trading script execution began"
    })

@csrf_exempt
def bot_status(request):
    """Check execution status"""
    return JsonResponse(bot_state)