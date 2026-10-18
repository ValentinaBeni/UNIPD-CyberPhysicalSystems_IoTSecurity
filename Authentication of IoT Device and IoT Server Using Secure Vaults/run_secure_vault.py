import os
from dotenv import load_dotenv
from Server import Server
from DeviceVault import DeviceVault
from Vault import Vault



if __name__ == "__main__":

    load_dotenv()
    number_of_keys = int(os.getenv("NUMBER_OF_KEYS"))
    key_size = int(os.getenv("KEY_SIZE"))
    challenge_1_length = int(os.getenv("CHALLENGE_1_LENGTH"))
    challenge_2_length = int(os.getenv("CHALLENGE_2_LENGTH"))
    number_of_runs = int(os.getenv("NUMBER_OF_RUNS"))

    evaluation = {}
    encrypt_times = []
    decrypt_times = []
    vault_times = []
    
    for id in range(number_of_runs):
        server = Server(challenge_1_length, key_size)
        server.start()

        vault = Vault(number_of_keys, key_size)
        device = DeviceVault(id, server, challenge_2_length, key_size, vault)
        device.start()
        device.join()
        server.join()

        status = "Success" if device.authenticated else "Failed"
        encrypt = f"{device.encrypt_time*1000:.4f}" if device.encrypt_time else "N/A"
        decrypt = f"{device.decrypt_time*1000:.4f}" if device.decrypt_time else "N/A"
        vault = f"{device.vault_update_time*1000:.4f}" if device.vault_update_time else "N/A"
        
        if device.authenticated:
            encrypt_times.append(device.encrypt_time)
            decrypt_times.append(device.decrypt_time)
            vault_times.append(device.vault_update_time)
        
        evaluation[device.device_id] = {
            "Encrypt (ms)": encrypt,
            "Decrypt (ms)": decrypt,
            "Vault Update (ms)": vault,
            "Status": status
        }

    # Calculate and display averages
    average_score = {}
    total_sum = 0.0
    encrypt_avg = decrypt_avg = vault_avg = 0.0

    if encrypt_times:
        encrypt_avg = sum(encrypt_times) * 1000 / len(encrypt_times)
        average_score["Encryption"] = f"{encrypt_avg:.4f}"
        total_sum += encrypt_avg

    if decrypt_times:
        decrypt_avg = sum(decrypt_times) * 1000 / len(decrypt_times)
        average_score["Decryption"] = f"{decrypt_avg:.4f}"
        total_sum += decrypt_avg

    if vault_times:
        vault_avg = sum(vault_times) * 1000 / len(vault_times)
        average_score["Vault Update"] = f"{vault_avg:.4f}"
        total_sum += vault_avg

    average_score["Total Time"] = f"{total_sum:.4f}"


    print("Average Performance Metrics:")
    for metric, avg_time in average_score.items():
        print(f"{metric}: {avg_time} ms")