import psutil
import pandas as pd

# Collect running services
services = []
for service in psutil.win_service_iter():
    try:
        s = service.as_dict()
        if s['status'] == 'running':
            services.append({
                "DisplayName": s['display_name'],
                "ServiceName": s['name'],
                "Status": s['status']
            })
    except Exception as e:
        pass

# Save to Excel
df = pd.DataFrame(services)
output_file = "C:/Users/shiva/Desktop/RunningServices.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Excel file created: {output_file}")
