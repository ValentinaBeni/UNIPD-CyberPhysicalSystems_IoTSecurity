from Server import Server
from DeviceECC import DeviceECC
from dotenv import load_dotenv
import os

if __name__ == "__main__":

    load_dotenv()
    number_of_runs = int(os.getenv("NUMBER_OF_RUNS"))

    

    key_gen_times = []
    sign_times = []
    verify_times = []
    total_times = []
    evaluation = {}

    for id in range(number_of_runs):
        server = Server()
        server.start()

        device = DeviceECC(id, server)
        device.start()
        device.join()
        server.join()

        status = "Success" if device.status == "Success" else "Failed"
        key_gen = f"{device.key_gen_time*1000:.4f}" if device.key_gen_time else "N/A"
        sign = f"{device.sign_time*1000:.4f}" if device.sign_time else "N/A"
        verify = f"{device.verify_time*1000:.4f}" if device.verify_time else "N/A"
        if device.key_gen_time is not None and device.sign_time is not None and device.verify_time is not None:
            total_time = f"{(device.key_gen_time + device.sign_time + device.verify_time):.4f}"  
        else:
            total_time = 0
        evaluation[device.device_id] = {
            "Key Gen (ms)": key_gen,
            "Sign (ms)": sign,
            "Verify (ms)": verify,
            "Total (ms)": total_time,
            "Status": status
        }
        if status == "Success":
            key_gen_times.append(device.key_gen_time)
            sign_times.append(device.sign_time)
            verify_times.append(device.verify_time)
            total_times.append(float(total_time))
        
    # Calculate and display averages
    average_score = {}
    if key_gen_times:
        key_gen_avg = sum(key_gen_times) * 1000 / len(key_gen_times)
        average_score["Key Generation"] = f"{key_gen_avg:.4f}"
    if sign_times:
        sign_avg = sum(sign_times) * 1000 / len(sign_times)
        average_score["Signing"] = f"{sign_avg:.4f}"
    if verify_times:
        verify_avg = sum(verify_times) * 1000 / len(verify_times)
        average_score["Verification"] = f"{verify_avg:.4f}"
    if total_times:
        total_avg = sum(total_times) * 1000 / len(total_times)
        average_score["Total"] = f"{total_avg:.4f}"

    print("----- Average Performance Metrics: -----")
    for metric, avg_time in average_score.items():
        print(f"{metric}: {avg_time} ms")