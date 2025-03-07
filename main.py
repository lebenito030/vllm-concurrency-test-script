import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any

async def send_request(session: aiohttp.ClientSession, url: str, prompt: str, request_id: int) -> Dict[str, Any]:
    """Send a request to the vLLM API and track performance metrics."""
    start_time = time.time()
    payload = {
        "model": "your_model_name",  # Replace with your actual model name
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "stream": False
    }
    
    try:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                return {
                    "success": False, 
                    "error": f"HTTP {response.status}: {error_text}", 
                    "request_id": request_id
                }
            
            result = await response.json()
            end_time = time.time()
            
            # Extract metrics
            input_tokens = result["usage"]["prompt_tokens"]
            output_tokens = result["usage"]["completion_tokens"]
            total_tokens = result["usage"]["total_tokens"]
            latency = end_time - start_time
            
            # Calculate token generation speed (tokens per second)
            token_speed = output_tokens / latency if latency > 0 else 0
            
            return {
                "success": True,
                "request_id": request_id,
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "token_speed": token_speed
            }
            
    except Exception as e:
        return {
            "success": False, 
            "error": str(e), 
            "request_id": request_id,
            "latency": time.time() - start_time
        }

async def run_concurrency_test(url: str, concurrency: int, prompt: str) -> Dict[str, Any]:
    """Run a concurrency test with the specified number of concurrent requests."""
    print(f"Starting test with {concurrency} concurrent requests...")
    
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, url, prompt, i) for i in range(concurrency)]
        results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    if successful_requests:
        latencies = [r["latency"] for r in successful_requests]
        token_speeds = [r["token_speed"] for r in successful_requests]
        total_output_tokens = sum(r["output_tokens"] for r in successful_requests)
        
        # Calculate aggregate metrics
        avg_latency = statistics.mean(latencies)
        avg_token_speed = statistics.mean(token_speeds)
        overall_token_speed = total_output_tokens / total_time
        
        return {
            "concurrency": concurrency,
            "total_requests": concurrency,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "avg_latency": avg_latency,
            "avg_token_speed": avg_token_speed,
            "overall_token_speed": overall_token_speed,
            "total_output_tokens": total_output_tokens,
            "p50_latency": sorted(latencies)[int(len(latencies) * 0.5)],
            "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)],
            "p99_latency": sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) >= 100 else None,
            "min_latency": min(latencies),
            "max_latency": max(latencies)
        }
    else:
        return {
            "concurrency": concurrency,
            "total_requests": concurrency,
            "successful_requests": 0,
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "error_sample": failed_requests[0]["error"] if failed_requests else "Unknown error"
        }

async def main():
    # Configuration
    url = "http://localhost:8000/v1/chat/completions"  # Update with your vLLM API endpoint
    concurrency = 500
    
    # Use a consistent prompt for all requests
    prompt = """
    Explain the concept of machine learning in a few sentences. 
    Keep your answer brief but informative.
    """
    
    # Run the test
    results = await run_concurrency_test(url, concurrency, prompt)
    
    # Print and save results
    print("\n==== Test Results ====")
    print(f"Concurrency level: {results['concurrency']}")
    print(f"Successful requests: {results['successful_requests']}/{results['total_requests']}")
    
    if results['successful_requests'] > 0:
        print(f"\nPerformance Metrics:")
        print(f"  Total time: {results['total_time']:.2f} seconds")
        print(f"  Average latency: {results['avg_latency']:.2f} seconds")
        print(f"  Average token speed: {results['avg_token_speed']:.2f} tokens/second")
        print(f"  Overall token generation speed: {results['overall_token_speed']:.2f} tokens/second")
        print(f"  P50 latency: {results['p50_latency']:.2f} seconds")
        print(f"  P95 latency: {results['p95_latency']:.2f} seconds")
        if results['p99_latency']:
            print(f"  P99 latency: {results['p99_latency']:.2f} seconds")
        print(f"  Total output tokens: {results['total_output_tokens']}")
    else:
        print(f"\nAll requests failed. Sample error: {results['error_sample']}")
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"vllm_concurrency_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())