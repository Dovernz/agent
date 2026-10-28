#!/usr/bin/env python3
"""
Hardware PSU Wattage and Compatibility Calculator
Calculates recommended Power Supply Unit (PSU) wattage based on CPU, GPU, and peripherals.
"""

import sys
import argparse

CPU_TDP = {
    "12400f": 65,
    "12400": 65,
    "12600kf": 125,
    "12600k": 125,
    "13400f": 65,
    "13400": 65,
    "13500": 65,
    "13600k": 125,
    "13600kf": 125,
    "14400f": 65,
    "14400": 65,
    "14500": 65,
    "14600k": 125,
    "5600": 65,
    "5600x": 65,
    "5700x": 65,
    "7600": 65,
    "7600x": 105,
    "7700x": 105,
    "9600x": 65,
}

CPU_PEAK_W = {
    "12400f": 117,
    "12600kf": 150,
    "13400f": 148,
    "13500": 154,
    "13600k": 181,
    "14400f": 148,
    "14500": 154,
    "14600k": 181,
    "5600": 88,
    "5700x": 88,
    "7600": 88,
    "7600x": 142,
}

GPU_TDP = {
    "gtx 1650": 75,
    "gtx 1660 super": 125,
    "rx 6500 xt": 107,
    "rx 6600": 132,
    "rtx 3050": 130,
    "rtx 3050 6gb": 70,
    "rtx 3060": 170,
    "rtx 4060": 115,
    "rtx 4060 ti": 160,
    "arc a380": 75,
    "arc a580": 185,
    "arc a750": 225,
}

def calculate_psu(cpu_name: str, gpu_name: str, num_ram_sticks=2, num_ssds=1, num_fans=4):
    cpu_key = cpu_name.lower().replace("intel", "").replace("core", "").replace("i5", "").replace("i7", "").replace("-", "").strip()
    gpu_key = gpu_name.lower().strip()

    cpu_tdp = CPU_PEAK_W.get(cpu_key, CPU_TDP.get(cpu_key, 120))
    gpu_tdp = GPU_TDP.get(gpu_key, 150)
    
    base_load = 50 + (num_ram_sticks * 5) + (num_ssds * 7) + (num_fans * 5)
    total_peak = cpu_tdp + gpu_tdp + base_load
    recommended_wattage = total_peak * 1.3
    
    standard_sizes = [450, 500, 550, 600, 650, 750, 850, 1000]
    final_psu = standard_sizes[-1]
    for size in standard_sizes:
        if size >= recommended_wattage:
            final_psu = size
            break

    return {
        "cpu": cpu_name,
        "cpu_peak_w": cpu_tdp,
        "gpu": gpu_name,
        "gpu_tdp_w": gpu_tdp,
        "base_load_w": base_load,
        "total_peak_draw_w": total_peak,
        "recommended_min_psu_w": final_psu,
        "recommended_certification": "80 Plus Bronze" if final_psu <= 650 else "80 Plus Gold",
        "sample_models": [
            f"MSI MAG A{final_psu}BN ({final_psu}W 80+ Bronze)",
            f"DeepCool PK{final_psu}D ({final_psu}W 80+ Bronze)",
            f"Cooler Master Elite V4 / MWE {final_psu}W"
        ]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate recommended PC PSU wattage")
    parser.add_argument("--cpu", type=str, default="13500", help="CPU model (e.g. 13500, 13400f, 12600kf)")
    parser.add_argument("--gpu", type=str, default="gtx 1650", help="GPU model (e.g. 'gtx 1650', 'rtx 3050 6gb')")
    parser.add_argument("--ram-sticks", type=int, default=2, help="Number of RAM sticks")
    parser.add_argument("--ssds", type=int, default=1, help="Number of NVMe SSDs")

    args = parser.parse_args()
    result = calculate_psu(args.cpu, args.gpu, args.ram_sticks, args.ssds)
    
    print("\n================ PC POWER SUPPLY RECOMMENDATION ================")
    print(f"CPU: {result['cpu']} (~{result['cpu_peak_w']}W peak)")
    print(f"GPU: {result['gpu']} (~{result['gpu_tdp_w']}W TDP)")
    print(f"Other components (Mainboard, RAM, SSD, Fans): ~{result['base_load_w']}W")
    print(f"Total Peak System Load: ~{result['total_peak_draw_w']}W")
    print("----------------------------------------------------------------")
    print(f"--> RECOMMENDED PSU RATING: {result['recommended_min_psu_w']}W ({result['recommended_certification']})")
    print("Suggested Popular Models in Vietnam:")
    for m in result['sample_models']:
        print(f"  - {m}")
    print("================================================================\n")
