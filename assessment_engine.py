"""Transparent prototype triage rules; scores are not diagnostic probabilities."""
PROFILES = {
 'Smartphone': ('Touchscreen response', 'Charging port', 'Camera operation'),
 'Laptop': ('Keyboard and trackpad', 'Charging port', 'Display output'),
 'Television': ('Display output', 'Audio output', 'Power stability'),
 'Monitor': ('Display output', 'Video input', 'Power stability'),
 'Desktop Computer': ('Boot and storage', 'Cooling system', 'Power supply'),
 'Printer': ('Paper feed', 'Print quality', 'Connection'),
 'Keyboard': ('Key response', 'Connection', 'Cable or port'),
 'Lithium-ion Battery': ('Charge retention', 'Terminal condition', 'Charging stability'),
}
PROFILES.update({
 'Tablet': ('Touchscreen response','Charging port','Camera operation'),
 'Smartwatch': ('Display and touch','Charging contacts','Buttons and sensors'),
 'Scanner': ('Scan output','Paper or lid mechanism','Connection'),
 'Mouse': ('Buttons and scroll wheel','Tracking sensor','Connection'),
 'Headphones / Earbuds': ('Audio in both channels','Microphone','Connection'),
 'Speaker': ('Audio output','Controls','Power and connection'),
 'Camera': ('Image capture','Lens operation','Storage and controls'),
 'Gaming Console': ('Boot and storage','Video output','Controller connection'),
 'Router / Modem': ('Power stability','Network connection','Ports'),
 'Power Bank': ('Charge retention','Output ports','Charging stability'),
 'Charger': ('Cable and insulation','Connector condition','Output operation'),
 'Refrigerator': ('Cooling performance','Door seal','Controls'),
 'Washing Machine': ('Drum operation','Drain and leak check','Controls'),
 'Air Conditioner': ('Cooling performance','Airflow','Controls'),
 'Microwave Oven': ('Door and latch condition','Controls','Reported heating operation'),
 'Other': ('Main function','Power or connection','Controls and enclosure'),
})
BATTERY_DEVICES={'Smartphone','Laptop','Tablet','Smartwatch','Headphones / Earbuds','Camera','Power Bank','Lithium-ion Battery'}

def evaluate(device,condition,functionality,battery,checks,hazard=False):
    values=[condition,functionality]+([battery] if battery is not None else [])
    score=round(sum(values)/len(values),1)
    failed=[name for name,state in checks.items() if state=='Failed']
    impaired=[name for name,state in checks.items() if state=='Impaired']
    unknown=[name for name,state in checks.items() if state=='Not checked']
    reasons=[]
    if hazard:
        route='Specialist handling';reasons.append('A damage or battery hazard was reported. Stop routine reuse assessment and arrange specialist inspection.')
        action='Do not charge, dismantle or ship the device until a qualified handler provides instructions.'
    elif condition<40 or functionality<20:
        route='Repairability inspection';reasons.append('Severe physical damage.' if condition<40 else 'Functionality is below 20: the device is not operational.')
        action='Assess repairability and recoverable parts before choosing refurbishment or recycling.'
    elif failed or functionality<55:
        route='Repair required';reasons.append('Failed checks: '+', '.join(failed)+'.' if failed else 'Functionality below 55 indicates impaired operation.')
        action='Repair and retest the affected functions before considering reuse.'
    elif battery is not None and battery<50:
        route='Battery service required';reasons.append('Battery health is below the prototype service threshold of 50.')
        action='Arrange battery inspection or replacement, then retest the device.'
    elif unknown:
        route='Inspection incomplete';reasons.append('Not checked: '+', '.join(unknown)+'.')
        action='Complete the device checks before making a reuse decision.'
    elif condition<75 or impaired or (battery is not None and battery<75):
        route='Refurbishment candidate';reasons.append('Cosmetic or functional wear needs attention before reuse.')
        action='Inspect, service and retest. Confirm repair cost and suitability for reuse.'
    else:
        route='Reuse candidate';reasons.append('Physical condition, operation and completed device checks meet the prototype reuse rules.')
        action='Complete a physical inspection and data-erasure checks where applicable before reuse.'
    if impaired: reasons.append('Impaired checks: '+', '.join(impaired)+'.')
    if unknown and route!='Inspection incomplete':reasons.append('Still unverified: '+', '.join(unknown)+'.')
    return {'route':route,'score':score,'reasons':reasons,'action':action}
