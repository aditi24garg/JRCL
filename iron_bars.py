from collections import Counter
bar_diameters = {
  (12,"A"):"10 mm",
  (12,"B"):"12 mm",
  (4,None):"10 mm"
  }
requirements={
    (12.0,"A"):[
     (3.52,1312),
     (2.67,1312),
     (2.23,2788),
     (1.62,1312),
     (1.3,656),
     (1.2,1640),
     (1.0,1148),],
     (12,"B"):[
       (1.62,1640)
       ]
       }

weight_per_meter = {
    "8 mm": 0.40,
    "10 mm": 0.62,
    "12 mm": 0.89,
    "16 mm": 1.58,
    "20 mm": 2.47,
    "25 mm": 3.86,
    "32 mm": 6.32,
    "36 mm": 8,
    "40 mm": 9.88
}

def process_stock(stock_length, requirement):
  pieces_left=[]
  for bar_length, count in requirement:
    pieces_left.extend([bar_length]*count)

  bars_used=0
  total_waste=0
  bars_cut_plan=[]
  total_weight_used = 0
  total_weight_wasted = 0

  # get weight per meter
  weight_per_m = weight_per_meter.get(diameter, 0) if diameter else 0

  tmp_pieces = pieces_left.copy()
  while tmp_pieces:
    bar_fill = 0
    used_pieces = []
    cut_this_bar = []
    for i, piece in enumerate(tmp_pieces):
      if bar_fill +piece<=stock_length:
        bar_fill+=piece
        used_pieces.append(i)
        cut_this_bar.append(piece)
    if not used_pieces:
      break
    for idx in reversed(used_pieces):
      tmp_pieces.pop(idx)
    bars_used+=1
    waste=stock_length-bar_fill
    total_waste+=waste
    bars_cut_plan.append(cut_this_bar)

    # weight calculation
    total_weight_used += bar_fill * weight_per_m
    total_weight_wasted += waste * weight_per_m

    plan_counter = Counter(tuple(sorted(cuts, reverse=True)) for cuts in bars_cut_plan)
    reusable_waste=0
    for plan, count in plan_counter.items():
      waste=stock_length-sum(plan)
      if waste>=1:
        reusable_waste+=count*waste
  percent_loss = (total_weight_wasted / (total_weight_used + total_weight_wasted) * 100) if (total_weight_used + total_weight_wasted) > 0 else 0  
  return{
"bars_used":bars_used,
"total_waste":total_waste,
"average_waste":(total_waste/bars_used) if bars_used else 0,
"plan_counter":plan_counter,
"stock_length":stock_length,
"reusable_waste":reusable_waste,
"unfulfilled_pieces": len(tmp_pieces),
"total_weight_used": total_weight_used,
"total_weight_wasted": total_weight_wasted,
"percent_loss": percent_loss
}
for stock_key,req in requirements.items():
  stock_length = stock_key[0]
  diameter = bar_diameters.get(stock_key,"N/A")
  print(f"\n==Stock Length:{stock_length}m (Diameter:{diameter})===")
  result=process_stock(stock_length,req)
  print(f"Total number of bars to order: {result['bars_used']}")
  print(f"Total Waste:{result['total_waste']:2f}meters")
  if result['bars_used']>0:
    print(f"Average wastage per bar:{result['average_waste']:2f}meters")
  if result['reusable_waste']>0:
    print(f"Out of total waste,{result['reusable_waste']:2f} meters can be reused (waste >= 1m from. individual bars.)")
  print("Cutting plan for each bar (grouped):")
  for plan, count in result['plan_counter'].items():
    cuts_str=','.join(f"{c:2f}" for c in plan)
    waste = stock_length - sum(plan)
    print(f"{count} bar(s):[{cuts_str}] | Waste:{waste:2f} m")
if result['unfulfilled_pieces']>0:
  print(f"Unfulfilled pieces:{result['unfulfilled_pieces']}(cannot fit in bars)")
