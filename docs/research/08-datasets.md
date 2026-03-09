# 08 — Structured Performance Data

## Purpose

This file contains structured, machine-readable performance data for earth-abundant electrocatalysts.
It is designed to be a starting point for ML training datasets.

All values are extracted from synthesis of published literature.
**Ranges reflect real experimental variance** — not just best reported values.
Use median of range as point estimate, full range as uncertainty.

---

## HER Performance Dataset

```csv
id,catalyst,class,electrolyte,pH_approx,eta_10_mV_low,eta_10_mV_high,tafel_mV_dec_low,tafel_mV_dec_high,stability_h,stability_note,cost_tier,acid_stable
H001,Pt/C,reference,0.5M H2SO4,0,30,50,28,35,>1000,gold standard,$$$$$,yes
H002,NiMo alloy,alloy,1M KOH,14,50,100,30,45,>10000,commercially deployed,$,no
H003,CoP nanoarrays,phosphide,0.5M H2SO4,0,67,110,50,70,24,moderate dissolution,$$,partial
H004,CoP nanoarrays,phosphide,1M KOH,14,100,150,55,75,100,good,$,no
H005,Ni2P,phosphide,0.5M H2SO4,0,100,140,46,65,10,poor acid stability,$,no
H006,Ni2P,phosphide,1M KOH,14,80,130,46,65,100,good,$,no
H007,FeP,phosphide,0.5M H2SO4,0,120,180,38,65,10,poor acid stability,$,no
H008,FeP,phosphide,1M KOH,14,100,150,45,70,50,moderate,$,no
H009,MoP,phosphide,0.5M H2SO4,0,90,130,45,55,20,moderate,$$,moderate
H010,WP,phosphide,0.5M H2SO4,0,120,160,45,65,50,good for non-PGM,$$$,good
H011,MoS2 (2H basal plane),sulfide,0.5M H2SO4,0,300,500,120,150,>100,stable but inactive,$,partial
H012,MoS2 (edge-rich),sulfide,0.5M H2SO4,0,150,250,55,80,50,moderate,$,partial
H013,1T-MoS2,sulfide,0.5M H2SO4,0,130,200,40,60,20,1T->2H conversion,$,partial
H014,Co-doped MoS2,sulfide,0.5M H2SO4,0,120,190,42,65,30,moderate,$,partial
H015,NiS2 (Ni foam),sulfide,1M KOH,14,150,230,60,90,50,moderate,$,no
H016,Mo2C,carbide,0.5M H2SO4,0,90,150,55,70,50,good,$$,good
H017,Mo2C@NC core-shell,carbide,0.5M H2SO4,0,80,130,50,65,100,good,$$,good
H018,WC nanostructured,carbide,0.5M H2SO4,0,100,170,50,80,50,good,$$$,good
H019,Mo2N,nitride,0.5M H2SO4,0,140,200,55,75,30,moderate,$$,moderate
H020,Ni3N,nitride,1M KOH,14,80,150,40,70,50,moderate,$,no
H021,Ni-Mo-N nanosheets,nitride,1M KOH,14,67,150,35,60,100,good,$,no
H022,FeNi intermetallic (ordered),intermetallic,1M KOH,14,80,130,35,55,200,good,$,no
H023,NiMoFe alloy,alloy,1M KOH,14,60,110,32,50,500,good,$,no
H024,Mo SAC @NC (Mo-N4),SAC,0.5M H2SO4,0,75,130,30,55,50,good,$$,good
H025,Co SAC @NC,SAC,0.5M H2SO4,0,100,160,35,60,30,moderate,$$,moderate
H026,Ni SAC @NC,SAC,1M KOH,14,80,150,38,65,30,moderate,$$,no
H027,Ti3C2 MXene + Mo2C,MXene composite,0.5M H2SO4,0,76,130,42,60,30,moderate,$$$,good
H028,N-P co-doped carbon,heteroatom carbon,1M KOH,14,200,350,80,120,200,excellent,$,no
H029,FeCoP ternary,phosphide,1M KOH,14,85,130,45,65,100,good,$,no
H030,CoMoP ternary,phosphide,0.5M H2SO4,0,75,120,45,60,50,moderate,$$,moderate
H031,CoP2 nanoarrays,phosphide,0.5M H2SO4,0,92,135,52,72,30,moderate dissolution,$$,partial
H032,Ni2P@NC encapsulated,phosphide,0.5M H2SO4,0,105,150,48,68,80,encapsulation improves acid stability,$$,good
H033,NiCoP ternary,phosphide,0.5M H2SO4,0,88,130,50,70,40,moderate,$,partial
H034,NiMoP ternary,phosphide,0.5M H2SO4,0,82,125,46,62,60,good for non-PGM,$$,moderate
H035,WC@NC core-shell,carbide,0.5M H2SO4,0,110,165,55,75,100,NC shell prevents dissolution,$$,good
H036,Mo2C nanotubes,carbide,0.5M H2SO4,0,98,148,50,70,60,higher surface area variant,$$,good
H037,CoS2 hollow spheres,sulfide,0.5M H2SO4,0,140,210,62,85,25,reconstructs to CoOOH-like,$,partial
H038,MoSe2 nanoflowers,selenide,0.5M H2SO4,0,155,230,65,90,30,selenide analogue of MoS2,$,partial
H039,WS2 edge-rich,sulfide,0.5M H2SO4,0,148,220,60,82,40,better activity than 2H-MoS2,$$,partial
H040,CoSe2 nanosheets,selenide,0.5M H2SO4,0,125,190,58,80,30,moderate activity and stability,$,partial
H041,Fe-N4 SAC,SAC,0.5M H2SO4,0,118,170,43,62,40,high mass activity potential,$$,moderate
H042,Co-N4 SAC,SAC,0.5M H2SO4,0,108,165,40,58,35,near-optimal HER binding,$$,moderate
H043,Ni-N4 SAC,SAC,0.5M H2SO4,0,128,180,48,67,30,moderate,$$,partial
H044,V2C MXene,MXene composite,0.5M H2SO4,0,115,175,52,72,35,new MXene class,$$$,moderate
H045,Ni3Se4 nanostructures,selenide,0.5M H2SO4,0,142,210,62,88,25,moderate activity,$,partial
H046,FeCoP ternary,phosphide,0.5M H2SO4,0,100,155,55,75,30,Fe destabilizes acid stability,$,partial
H047,Co4N nanowires,nitride,0.5M H2SO4,0,132,195,58,80,25,nitride dissolves in acid,$$,moderate
H048,FeP2 on carbon,phosphide,0.5M H2SO4,0,160,235,65,90,15,poor acid stability ($),$,partial
H049,CoMoS2 ternary,sulfide,0.5M H2SO4,0,135,200,58,80,35,ternary benefits vs binary,$,partial
H050,Mn-N4 SAC,SAC,0.5M H2SO4,0,140,210,52,75,30,Mn-N4 less active than Co-N4,$$,partial
H051,NbC nanoparticles,carbide,0.5M H2SO4,0,125,180,58,80,45,Nb carbide good acid stability,$$$,good
H052,VC nanostructures,carbide,0.5M H2SO4,0,135,195,60,82,40,moderate,$$,moderate
H053,MoP@C core-shell,phosphide,0.5M H2SO4,0,78,122,44,60,70,carbon shell protection,$$,moderate
H054,NiCoP@NC (acid),phosphide,0.5M H2SO4,0,85,128,48,66,50,ternary + encapsulation,$$,good
H055,W-doped CoP,phosphide,0.5M H2SO4,0,80,125,45,63,55,W improves acid stability,$$,moderate
H056,NiCoP ternary,phosphide,1M KOH,14,105,155,52,72,80,good stability,$,no
H057,NiFeP ternary,phosphide,1M KOH,14,92,140,46,65,100,NiFeP pre-catalyst,$,no
H058,FeCoP ternary,phosphide,1M KOH,14,100,148,50,70,80,good,$,no
H059,NiMo@NC alloy,alloy,1M KOH,14,65,105,34,52,200,NC support improves durability,$,no
H060,CoMoN nanosheets,nitride,1M KOH,14,82,128,40,60,100,good,$,no
H061,Co4N nanowires,nitride,1M KOH,14,88,135,38,60,100,good OER pre-catalyst,$,no
H062,Fe2N@NC,nitride,1M KOH,14,108,160,48,68,80,good,$,no
H063,CoSe2 alkaline,selenide,1M KOH,14,112,165,50,72,60,moderate,$,no
H064,NiSe2 alkaline,selenide,1M KOH,14,118,175,52,75,60,moderate,$,no
H065,NiCoSe2 ternary,selenide,1M KOH,14,100,150,48,68,80,ternary synergy,$,no
H066,Ti3C2 MXene,MXene composite,1M KOH,14,128,190,56,78,40,moderate,$$$,no
H067,NiCo alloy,alloy,1M KOH,14,82,128,38,58,500,excellent commercial stability,$,no
H068,NiFeCo ternary alloy,alloy,1M KOH,14,75,118,36,55,300,excellent,$,no
H069,NiMoW alloy,alloy,1M KOH,14,62,100,32,50,1000,near-commercial,$$,no
H070,NiCoMo alloy,alloy,1M KOH,14,70,110,34,52,800,excellent,$,no
H071,NiS2 on Ni foam,sulfide,1M KOH,14,140,210,58,85,50,reconstructs in situ,$,no
H072,Fe3S4 magnetic,sulfide,1M KOH,14,160,240,65,92,30,moderate,$,no
H073,Ni3N@NC,nitride,1M KOH,14,78,125,38,58,120,nitrogen-rich,$,no
H074,Cu-N4 SAC,SAC,0.5M H2SO4,0,148,220,55,80,20,low activity high selectivity,$$,partial
H075,NiCo2P heterojunction,phosphide,1M KOH,14,95,140,48,68,90,heterojunction synergy,$$,no
```

---

## OER Performance Dataset

```csv
id,catalyst,class,electrolyte,pH_approx,eta_10_mV_low,eta_10_mV_high,tafel_mV_dec_low,tafel_mV_dec_high,stability_h,stability_note,cost_tier,acid_stable
O001,IrO2,reference,0.5M H2SO4,0,250,320,40,60,>5000,industrial standard,$$$$$,yes
O002,RuO2,reference,0.5M H2SO4,0,200,280,40,60,200,dissolves slowly,$$$$$,partial
O003,IrO2,reference,1M KOH,14,270,350,45,65,>1000,gold standard alkaline,$$$$$,yes
O004,NiFe LDH,LDH,1M KOH,14,230,280,38,55,100,good,$,no
O005,NiFeV LDH,LDH,1M KOH,14,195,240,35,50,50,reported record,$,no
O006,NiCo LDH,LDH,1M KOH,14,270,320,45,65,50,moderate,$,no
O007,CoAl LDH,LDH,1M KOH,14,290,360,50,75,30,moderate,$,no
O008,BSCF perovskite,perovskite,1M KOH,14,230,270,60,80,20,amorphizes in use,$$,no
O009,LaCoO3,perovskite,1M KOH,14,350,430,60,90,50,moderate,$$,no
O010,PrBaCoO3 (PBC),perovskite,1M KOH,14,220,260,55,80,20,amorphizes,$$,no
O011,NiCo2O4 nanoarrays,spinel,1M KOH,14,280,340,60,80,50,moderate,$,no
O012,CoFe2O4,spinel,1M KOH,14,300,380,65,90,30,moderate,$,no
O013,CuCo2O4,spinel,1M KOH,14,320,400,65,95,20,moderate,$,no
O014,Co3O4 on graphene,oxide,1M KOH,14,300,400,60,70,50,moderate,$,no
O015,NiOOH (in situ),oxyhydroxide,1M KOH,14,260,310,40,65,100,good (active phase),$,no
O016,MnO2 (birnessite),oxide,1M KOH,14,350,500,70,100,50,moderate,$,partial
O017,MnO2 (birnessite),oxide,0.5M H2SO4,0,400,600,80,120,5,best acid option,$,poor
O018,Ca-MnO2 (birnessite),oxide,0.5M H2SO4,0,380,550,75,115,10,slightly better than MnO2,$,poor
O019,FeCoNiCrMn HEO,high-entropy,1M KOH,14,240,300,45,70,50,moderate,$$,no
O020,FeCoNi HEA (acid),high-entropy,0.5M H2SO4,0,350,450,60,90,10,best acid non-PGM,$$,poor
O021,FeCoNiCr (Cr-protected),high-entropy,0.5M H2SO4,0,370,480,65,95,30,moderate,$$,poor
O022,ZIF-67 derived Co@NC,MOF-derived,1M KOH,14,310,380,65,90,50,moderate,$$,no
O023,NiFeP,phosphide,1M KOH,14,250,300,45,65,100,phosphide pre-catalyst,$,no
O024,CoS2,sulfide,1M KOH,14,300,380,60,85,30,reconstructs to CoOOH,$,no
O025,Amorphous NiFeO_xH_y (electrodeposited),amorphous,1M KOH,14,240,280,40,60,200,practical synthesis,$,no
O026,Electrodeposited NiCoFe,amorphous,1M KOH,14,255,295,42,62,100,scalable,$$,no
O027,MnO2 + 3% Ru,doped oxide,0.5M H2SO4,0,320,430,65,100,20,better than pure MnO2,$$$,poor
O028,NiFe LDH exfoliated monolayer,LDH,1M KOH,14,210,260,35,50,30,high activity but fragile,$,no
O029,NiFe LDH + CNT,composite,1M KOH,14,225,270,37,52,100,improved conductivity,$,no
O030,FeCoNiCrMnTiV HEO,high-entropy 7-element,1M KOH,14,230,280,40,65,30,unexplored,$$$,no
O031,NiAl LDH,LDH,1M KOH,14,305,380,62,85,40,Al lacks redox activity,$,no
O032,CoFe LDH,LDH,1M KOH,14,315,390,64,88,40,moderate,$,no
O033,NiFeMn LDH,LDH,1M KOH,14,235,280,38,55,80,Mn promotes stability,$,no
O034,NiFeAl LDH,LDH,1M KOH,14,244,285,40,58,70,good,$,no
O035,NiFeV LDH exfoliated monolayer,LDH,1M KOH,14,204,248,34,50,30,highest activity fragile,$,no
O036,NiFeZn LDH,LDH,1M KOH,14,255,298,42,60,55,moderate,$,no
O037,NiCuFe LDH,LDH,1M KOH,14,262,308,44,64,45,Cu does not enhance much,$,no
O038,NiFe LDH + rGO,composite,1M KOH,14,220,265,36,52,80,CNT/rGO improves conductivity,$,no
O039,SrCoO3 perovskite,perovskite,1M KOH,14,285,350,63,85,15,amorphizes in <20h,$$,no
O040,La0.5Sr0.5CoO3,perovskite,1M KOH,14,335,415,68,90,30,moderate amorphization,$$,no
O041,LaNiO3,perovskite,1M KOH,14,345,430,72,95,40,moderate,$$,no
O042,NdBaCoO3 double perovskite,perovskite,1M KOH,14,245,295,58,82,15,LOM active amorphizes,$$,no
O043,SmBaCoO3,perovskite,1M KOH,14,255,308,60,84,20,amorphizes,$$,no
O044,MnCo2O4 nanoarray,spinel,1M KOH,14,315,390,68,90,40,moderate,$,no
O045,ZnCo2O4 spinel,spinel,1M KOH,14,355,440,72,95,30,moderate,$,no
O046,MnFe2O4 spinel,spinel,1M KOH,14,365,455,76,100,30,moderate,$,no
O047,NiMn2O4 spinel,spinel,1M KOH,14,335,415,70,92,35,moderate,$,no
O048,CoMn2O4 spinel,spinel,1M KOH,14,348,430,72,95,30,moderate,$,no
O049,Co3O4 nanoparticles,oxide,1M KOH,14,338,420,66,88,50,common reference,$,no
O050,NiCoFe amorphous,amorphous,1M KOH,14,244,290,43,62,150,ternary amorphous good,$$,no
O051,NiFeMo amorphous,amorphous,1M KOH,14,228,272,39,58,180,Mo enhances stability,$$,no
O052,CoPi cobalt phosphate,phosphate,1M KOH,14,318,395,68,90,60,self-healing in phosphate,$,no
O053,NiB amorphous film,amorphous,1M KOH,14,275,335,50,72,100,boride promotes activity,$,no
O054,Electrodeposited NiMoFe,amorphous,1M KOH,14,238,280,40,60,120,scalable synthesis,$$,no
O055,NiFeOOH in-situ,oxyhydroxide,1M KOH,14,245,290,40,60,120,NiFe LDH active phase,$,no
O056,CoFe2O4 spinel,spinel,1M KOH,14,335,410,68,90,35,moderate,$,no
O057,FeCoNiCrTi HEO,high-entropy,1M KOH,14,255,305,48,68,60,5-element Ti addition,$$,no
O058,FeCoNiMnAl HEO,high-entropy,1M KOH,14,265,318,52,72,45,Al destabilizes slightly,$$,no
O059,ZIF-67 Co@NC MOF-derived,MOF-derived,1M KOH,14,308,382,64,88,60,good,$$,no
O060,NiCo@NC MOF-derived,MOF-derived,1M KOH,14,295,368,60,84,70,good,$$,no
O061,FeNi@NC MOF-derived,MOF-derived,1M KOH,14,285,355,58,82,70,good,$$,no
O062,NiFeV LDH 5% V,LDH,1M KOH,14,212,255,36,52,45,V loading optimized,$$,no
O063,NiFeV LDH 15% V,LDH,1M KOH,14,230,272,38,55,35,too much V hurts stability,$$,no
O064,BSCF after 100h (aged),perovskite,1M KOH,14,270,320,55,78,100,amorphized + stabilized,$$,no
O065,NiOx (anodic deposit),oxide,1M KOH,14,280,340,48,68,80,simple electrodeposition,$,no
O066,SnO2-doped MnO2,doped oxide,0.5M H2SO4,0,445,580,108,140,8,slight improvement vs MnO2,$$,poor
O067,TiO2-MnO2 composite,composite,0.5M H2SO4,0,475,620,112,145,6,poor stability,$$,poor
O068,FeCoNiCrMo HEA,high-entropy,0.5M H2SO4,0,375,480,68,95,20,best 5-el acid non-PGM,$$,poor
O069,FeCoNiCrW HEA,high-entropy,0.5M H2SO4,0,365,468,65,92,25,W improves slightly,$$,poor
O070,Mn3O4 spinel acid,oxide,0.5M H2SO4,0,545,700,128,165,3,very poor acid stability,$,poor
O071,Ca-birnessite 5% Ca,doped oxide,0.5M H2SO4,0,415,540,92,125,12,modest improvement,$$,poor
O072,Mn-V oxide acid,doped oxide,0.5M H2SO4,0,455,590,106,138,8,V stabilizes Mn slightly,$$,poor
O073,FeCoNiCrMnV HEA 6-element,high-entropy,0.5M H2SO4,0,355,455,62,88,30,best 6-el acid non-PGM,$$,poor
O074,WO3-modified MnO2,composite,0.5M H2SO4,0,490,640,118,150,4,very poor,$$,poor
O075,Ca-Mn-Ru-Ox 3% Ru,doped oxide,0.5M H2SO4,0,340,440,70,105,35,best Mn-based acid option,$$$,poor
```

---

## Full-Cell (Two-Electrode) Performance Dataset

```csv
id,anode_catalyst,cathode_catalyst,electrolyte,j_mA_cm2,cell_voltage_V_low,cell_voltage_V_high,stability_h,notes
FC001,IrO2,Pt/C,0.5M H2SO4,10,1.47,1.52,>1000,PEM reference
FC002,IrO2,Pt/C,1M KOH,10,1.51,1.55,>1000,alkaline reference
FC003,NiFe LDH,CoP,1M KOH,10,1.56,1.68,50,top lab performer
FC004,NiMoP,NiFe LDH,1M KOH,10,1.58,1.70,100,bifunctional
FC005,NiCo2O4,Ni2P,1M KOH,10,1.60,1.72,50,moderate
FC006,NiFe LDH,NiMo alloy,1M KOH,10,1.58,1.68,200,near-industrial
FC007,Commercial NiFe,NiMo,30% KOH,400,1.85,2.05,>50000,commercial AEL baseline
FC008,NiFeV LDH,CoP,1M KOH,10,1.53,1.62,30,record claim
FC009,Amorphous NiFeO_xH_y,Ni-Mo-N,1M KOH,10,1.55,1.65,100,practical synthesis both
FC010,FeCoNiCr HEA,Mo2C@NC,0.5M H2SO4,10,1.72,1.88,10,acid best non-PGM
```

---

## Synthesis Conditions Dataset

```csv
id,catalyst,synthesis_method,temperature_C,time_h,key_precursors,atmosphere,substrate,yield_mg_cm2
S001,CoP nanoarrays,hydrothermal + phosphidation,"180,350","12,2","CoCl2, NaH2PO2",Ar,carbon cloth,2-5
S002,Ni2P,TOP reduction,300,1,"Ni(acac)2, TOP",N2,glassy carbon,3-8
S003,NiFe LDH,hydrothermal,120,12,"Ni(NO3)2, Fe(NO3)3, urea",air,Ni foam,5-15
S004,NiFeV LDH,coprecipitation,80,6,"NiSO4, FeSO4, VOSO4, NaOH",N2,FTO,2-8
S005,1T-MoS2,hydrothermal + n-BuLi,220,24,"MoS2, n-butyllithium",N2,Si/SiO2,1-3
S006,Mo2C@NC,pyrolysis,"800 (carburization)",2,"(NH4)6Mo7O24, glucose",N2/CH4,none (powder),bulk
S007,Mo SAC@NC,pyrolysis,900,2,"(NH4)6Mo7O24, ZIF-8",Ar,none (powder),bulk
S008,BSCF perovskite,sol-gel + calcination,"1000-1100",5,"Ba(NO3)2, Sr(NO3)2, Co(NO3)2, Fe(NO3)3",air,FTO,5-20
S009,Amorphous NiFeO_xH_y,electrodeposition,25,0.5,"NiSO4, FeSO4",N2 purged,Ni foam,2-8
S010,FeCoNiCrMn HEO,ball milling + oxidation,"800",4,"Fe, Co, Ni, Cr, Mn powders",air,none,bulk
S011,NiMo alloy,electrodeposition or sputtering,25-200,1-10,"NiSO4, (NH4)6Mo7O24",H2 (for reduction),Ni foam / Ti,5-50
S012,MnO2 birnessite,hydrothermal,120,12,"KMnO4, MnSO4",none,FTO,3-10
S013,NiCo2O4 nanowires,hydrothermal + calcination,"180, 300","12, 2","Ni(NO3)2, Co(NO3)2, urea",air,Ni foam,3-10
S014,Co3O4 on graphene,hydrothermal + calcination,"180, 350",12,"CoCl2, graphene oxide",air,GCE,5-15
S015,FeP on carbon cloth,hydrothermal + phosphidation,"180, 400","12, 2","FeCl3, NaH2PO2",Ar,carbon cloth,2-6
```

---

## Selenide Catalyst Dataset (New Class — High Growth Area)

```csv
id,catalyst,class,reaction,electrolyte,eta_10_mV_low,eta_10_mV_high,tafel_mV_dec_low,tafel_mV_dec_high,stability_h,notes,cost_tier
SE001,CoSe2 nanostructures,selenide,HER,0.5M H2SO4,125,190,58,80,30,moderate - better than CoS2,$
SE002,NiSe2 nanosheet,selenide,HER,1M KOH,118,175,52,75,60,moderate,$
SE003,MoSe2 basal plane,selenide,HER,0.5M H2SO4,280,450,115,145,30,low basal activity,$
SE004,MoSe2 edge-rich,selenide,HER,0.5M H2SO4,155,230,65,90,30,similar to MoS2 edge,$
SE005,WSe2 edge-rich,selenide,HER,0.5M H2SO4,180,260,68,95,25,tungsten Se analogue,$$
SE006,FeSe2 pyrite,selenide,HER,0.5M H2SO4,175,250,65,88,20,poor acid stability,$
SE007,CoSe2 on carbon cloth,selenide,OER,1M KOH,290,360,60,82,40,reconstructs to CoOOH,$
SE008,NiSe2 on Ni foam,selenide,OER,1M KOH,280,345,58,80,50,moderate,$
SE009,NiCoSe2 ternary,selenide,HER,1M KOH,100,150,48,68,80,ternary synergy,$
SE010,Ni3Se4 nanostructures,selenide,HER,0.5M H2SO4,142,210,62,88,25,Ni-rich phase,$
```

## Molecular Catalyst Dataset (Emerging — Controlled Active Sites)

```csv
id,catalyst,class,electrolyte,eta_10_mV,tafel_mV_dec,stability_h,notes,cost_tier
M001,Co-porphyrin@CNT,molecular OER,1M KOH,420,85,10,poor stability but controlled site,$$
M002,Fe-porphyrin@graphene,molecular OER,1M KOH,440,90,8,very poor stability,$$
M003,Mn-porphyrin@CNT,molecular OER,1M KOH,480,98,5,poor,$$
M004,Co-phthalocyanine@NC,molecular HER,0.5M H2SO4,210,78,15,poor acid stability,$$
M005,[Ru(bda)] on CNT,molecular OER,pH 7,350,72,30,best molecular OER,$$$
M006,Co-corrole@graphene,molecular OER,1M KOH,460,95,8,poor stability,$$
M007,Mn4O4 cubane on ITO,cubane OER,1M KOH,480,100,15,model of PSII,$$$$
M008,Cofacial Co-porphyrin dimer,molecular OER,1M KOH,380,78,5,dual-site O-O: best activity,$$$
M009,Fe-corrole on GCE,molecular OER,0.5M H2SO4,440,88,3,very poor acid stability,$$
M010,Ni-cyclam@electrode,molecular HER,0.5M H2SO4,280,85,5,model system not practical,$$
```

## Updated Synthesis Conditions Dataset (Extended)

```csv
id,catalyst,synthesis_method,temperature_C,time_h,key_precursors,atmosphere,substrate,yield_mg_cm2
S001,CoP nanoarrays,hydrothermal + phosphidation,"180,350","12,2","CoCl2, NaH2PO2",Ar,carbon cloth,2-5
S002,Ni2P,TOP reduction,300,1,"Ni(acac)2, TOP",N2,glassy carbon,3-8
S003,NiFe LDH,hydrothermal,120,12,"Ni(NO3)2, Fe(NO3)3, urea",air,Ni foam,5-15
S004,NiFeV LDH,coprecipitation,80,6,"NiSO4, FeSO4, VOSO4, NaOH",N2,FTO,2-8
S005,1T-MoS2,hydrothermal + n-BuLi,220,24,"MoS2, n-butyllithium",N2,Si/SiO2,1-3
S006,Mo2C@NC,pyrolysis,"800 (carburization)",2,"(NH4)6Mo7O24, glucose",N2/CH4,none (powder),bulk
S007,Mo SAC@NC,pyrolysis,900,2,"(NH4)6Mo7O24, ZIF-8",Ar,none (powder),bulk
S008,BSCF perovskite,sol-gel + calcination,"1000-1100",5,"Ba(NO3)2, Sr(NO3)2, Co(NO3)2, Fe(NO3)3",air,FTO,5-20
S009,Amorphous NiFeO_xH_y,electrodeposition,25,0.5,"NiSO4, FeSO4",N2 purged,Ni foam,2-8
S010,FeCoNiCrMn HEO,ball milling + oxidation,"800",4,"Fe, Co, Ni, Cr, Mn powders",air,none,bulk
S011,NiMo alloy,electrodeposition or sputtering,25-200,1-10,"NiSO4, (NH4)6Mo7O24",H2 (for reduction),Ni foam / Ti,5-50
S012,MnO2 birnessite,hydrothermal,120,12,"KMnO4, MnSO4",none,FTO,3-10
S013,NiCo2O4 nanowires,hydrothermal + calcination,"180, 300","12, 2","Ni(NO3)2, Co(NO3)2, urea",air,Ni foam,3-10
S014,Co3O4 on graphene,hydrothermal + calcination,"180, 350",12,"CoCl2, graphene oxide",air,GCE,5-15
S015,FeP on carbon cloth,hydrothermal + phosphidation,"180, 400","12, 2","FeCl3, NaH2PO2",Ar,carbon cloth,2-6
S016,CoSe2 nanostructures,hydrothermal + Se reduction,180,12,"CoCl2, Se powder",N2,carbon cloth,2-6
S017,MoSe2 edge-rich,hydrothermal,200,18,"(NH4)6Mo7O24, Se powder, N2H4",N2,GCE,1-3
S018,Ni2P@NC encapsulated,ZIF-8 template + phosphidation,"300, 400","6, 2","Ni(acac)2, ZIF-8, NaH2PO2",Ar,FTO,3-8
S019,Fe-N4 SAC,pyrolysis of Fe-porphyrin@NC,900,2,"FeTPP, ZIF-8, NH3",N2/NH3,none,bulk
S020,NiCoP ternary,hydrothermal + phosphidation,"160, 350","12, 2","NiSO4, CoCl2, NaH2PO2",Ar,Ni foam,3-8
S021,NiFeMo amorphous,galvanostatic electrodeposition,25,0.5,"NiSO4, FeSO4, (NH4)6Mo7O24",N2,Ni foam,2-8
S022,Co4N nanowires,hydrothermal + nitridation,"180, 400","12, 2","Co(NO3)2, melamine",NH3,carbon cloth,2-5
S023,La0.5Sr0.5CoO3,Pechini method + calcination,1100,8,"La(NO3)3, Sr(NO3)2, Co(NO3)2",air,FTO,5-20
S024,ZIF-67 derived Co@NC,pyrolysis of ZIF-67,900,2,"ZIF-67",N2,none,bulk
S025,NiFeV LDH exfoliated,sonication + formamide intercalation,25,24,"NiFeV LDH powder, formamide",N2,FTO,0.5-2
S026,Ca-Mn-Ru-Ox,sol-gel + calcination,"550",4,"Ca(NO3)2, KMnO4, RuCl3",air,Ti mesh,2-8
S027,WC@NC core-shell,impregnation + carburization,900,3,"WCl6, ZIF-8 carbon",CH4/H2,none,bulk
S028,NiMo@NC alloy,co-reduction + pyrolysis,800,2,"NiSO4, (NH4)6Mo7O24, ZIF-8",H2/N2,none,bulk
S029,NiCo alloy film,electrodeposition (controlled),25,2,"NiSO4, CoSO4, boric acid",none,Ni foam,10-30
S030,CoFe LDH,coprecipitation at pH 9,60,4,"CoCl2, FeCl3, NaOH",N2,FTO,3-10
```

---

## Feature Engineering Reference

Descriptor features commonly used in ML models for catalyst activity:

```csv
feature_name,feature_type,description,data_source,relevance
d_band_center,electronic,"Center of d-band density of states",DFT,HER and OER volcano position
work_function,electronic,Electron work function in eV,DFT/experiment,charge transfer tendency
electronegativity_avg,compositional,Pauling electronegativity average,elemental tables,M-O bond character
ionic_radius_avg,structural,Average ionic radius of active metal,elemental tables,lattice parameter
oxide_formation_energy,thermodynamic,Energy to form bulk oxide per atom,DFT/NIST,stability proxy
Pourbaix_stable_window,thermodynamic,pH range where oxide is stable,Pourbaix diagram,dissolution resistance
M_O_bond_energy,thermodynamic,Metal-oxygen bond dissociation energy,DFT,OER intermediate binding
M_H_bond_energy,thermodynamic,Metal-hydrogen bond dissociation energy,DFT,HER Sabatier descriptor
ECSA_cm2,structural,Electrochemical surface area per geometric area,experiment,normalize activity
BET_m2_g,structural,BET surface area,experiment,porosity
crystallite_size_nm,structural,XRD Scherrer crystallite size,experiment,particle size effect
eg_electrons,electronic,Occupancy of eg antibonding orbitals,DFT/experiment,OER perovskite descriptor
charge_transfer_resistance,kinetic,Rct from EIS Nyquist fit,experiment,kinetics at electrode
dissolution_potential_V,thermodynamic,Potential at which M dissolves in Pourbaix,Pourbaix diagram,stability
```

---

## Known Performance Contradictions in Literature

These discrepancies are worth investigating — they likely reveal important synthesis-performance relationships:

| Catalyst | Group A result | Group B result | Likely reason |
|----------|---------------|---------------|---------------|
| NiFe LDH η₁₀ (1M KOH) | 270 mV | 230 mV | KOH Fe impurity content |
| 1T-MoS₂ η₁₀ (acid) | 130 mV | 200 mV | % 1T phase retention |
| BSCF η₁₀ | 230 mV | 320 mV | Amorphization during prep |
| CoP η₁₀ (acid) | 67 mV | 140 mV | Loading, substrate, ECSA normalization |
| NiFeV LDH η₁₀ | 195 mV | 260 mV | V content, synthesis route |
| Mo SAC@NC | 75 mV | 180 mV | True single-atom vs. clusters |

**Note on KOH purity:** Multiple studies show "pure" Ni(OH)₂ OER activity varies by
>50 mV between labs using "99.9% KOH" — because Fe impurity content varies 1–100 ppm
between suppliers. A 10 ppm Fe in 1M KOH deposits enough Fe to activate NiOOH.
Always specify KOH source and purification in methods.
