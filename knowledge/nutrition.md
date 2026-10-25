# Nutrition and diets

> Part of the coach's knowledge base. Loaded on demand by the coach commands (/plan, /review, /menu, /setup). Rules, not a literature review. Source IDs refer to knowledge/sources.md. Evidence checked on 2026-10-24.

## How to read this file

Each rule carries an evidence grade. **Strong**: consistent results from systematic reviews or meta-analyses of good trials, or from major guidelines, so act on it by default. **Moderate**: supported by meta-analyses or guidelines with real limits (few trials, heterogeneity, indirect populations), so apply it but expect exceptions. **Emerging**: small or single studies, narrative reviews, observational data or expert opinion, so use it as a reasonable default and never present it as settled. The evidence comes mostly from adults with overweight or obesity, young men, athletes, or specific national populations; for ordinary gym-goers many rules are extrapolations, as stated under "Applies to". Every estimate in this file is a starting point to be corrected by the client's own data.

## Key rules at a glance

- Estimate RMR with Mifflin-St Jeor, treat it as ±10%, and recalibrate from the client's weight trend after 2-4 weeks. (moderate) [S161], [S267], [S287], [S288], [S819]
- Use activity multipliers of about 1.4-1.5 for desk workers, never 1.2 for ambulatory adults, and not above about 2.0 for recreational lifters. (moderate) [S166], [S281]
- Weight loss slows as weight falls; never promise linear loss from the 3500 kcal (7700 kcal/kg) rule. (moderate) [S159], [S292], [S293]
- For fat loss in overweight adults, use a deficit of about 500-750 kcal/day. (strong) [S167]
- When keeping or building muscle is the goal, keep the deficit at or below about 500 kcal/day. (moderate) [S169]
- Protein for people who lift: about 1.6 g/kg/day is the estimate where extra protein stops adding measurable fat-free mass; range 1.4-2.2, upper end useful in a deficit. (moderate) [S185], [S186], [S187]
- At least 0.83 g/kg/day protein for any adult. (strong) [S795], [S183]
- Older adults (65+): protein at least 1.0-1.2 g/kg/day, 1.2-1.6 g/kg/day when lifting, always with resistance training; no deficit unless obesity with a weight-related health problem. (moderate) [S192], [S193], [S187], [S173], [S668]
- Low-carb and low-fat give similar weight loss when calories are matched; choose the pattern the client can sustain. (strong) [S208], [S209], [S210], [S216]
- Keep fat at or above about 20% of energy, fibre at or above 25 g/day, and free sugars below 10% of energy. (strong) [S325], [S330], [S206], [S338]
- Food logs under-report intake by roughly 10-30%; judge energy balance from the weight trend, not the log. (strong) [S295], [S289], [S296]
- At /setup, ask a few brief SCOFF-style questions as a prompt, never a diagnosis; any positive answer or warning sign means no deficit, no weight targets, no weigh-ins, and a GP or eating-disorder professional. (moderate) [S349], [S350]
- Creatine monohydrate 3-5 g/day is the first supplement to suggest to lifters. (strong) [S242], [S243], [S244]
- Creatine loading is optional; expect 1-3 kg of early water weight if loading; no good evidence of hair loss, dehydration or cramps. (moderate) [S244]
- Most "fat burners" and BCAAs are not worth buying. (moderate) [S256], [S257], [S258]
- Never prescribe below about 1,200 kcal/day for women or 1,500 kcal/day for men without clinical supervision; VLCD (<800 kcal/day) only under medical supervision. (strong) [S359], [S360]
- Any new missed or irregular period, low libido, recurring stress fractures or persistent fatigue during a diet: stop increasing the deficit, ask about intake and recommend a GP; 3+ months without periods or fewer than 6 a year: stop the deficit and refer. (moderate) [S336], [S348]
- GLP-1 or tirzepatide users: no coach-imposed extra deficit; the prescriber owns the weight plan; coach resistance training, protein 1.2-1.6 g/kg/day and red flags. (moderate) [S361]
- No amount of alcohol is protective; count it at 7 kcal/g. (strong) [S259], [S316]
- Budget for the extra food that drinking triggers, about 250+ kcal per occasion in total. (moderate) [S393]

## Estimating energy needs

### Default RMR equation: Mifflin-St Jeor
**Rule:** Use Mifflin-St Jeor (MSJ) as the default starting RMR for ordinary adults, especially when body composition is unknown or unreliable. MSJ in its sex-specific form: RMR (kcal/day) = 10 × weight (kg) + 6.25 × height (cm) - 5 × age (y) + 5 for men, and the same with - 161 instead of + 5 for women. Present the result to the client as a starting guess with about ±10% error (roughly ±150-200 kcal for a typical adult), not a measurement, and calibrate it against the real 2-4-week weight trend.
**Evidence:** A systematic review of the four most-used equations (Harris-Benedict, MSJ, Owen, WHO/FAO/UNU) in healthy non-obese and obese adults found MSJ estimated RMR within 10% of measured in more people than any other, with the narrowest error range. In 337 community-living adults, MSJ was unbiased (95% CI of the difference -26 to +8 kcal/d) and 82% of estimates fell within ±10% (87% non-obese, 75% obese); Livingston performed similarly (79%), while Harris-Benedict, WHO and others tended to overestimate. About 1 in 5 people are still off by more than 10%. MSJ was derived from 498 healthy adults (247 women, 251 men, aged 19-78, normal weight and obese; R2 0.71), and the simplified sex-specific form predicted as well as the full equation.
**Grade:** moderate
**Applies to:** Healthy ambulatory adults, normal weight to obesity, mostly white North American samples. Not validated for severe obesity, clinical populations, athletes, older adults or many ethnic groups, which were under-represented.
**Individual variation / conflicts:** Group bias is near zero but individual error is large and unpredictable. Accuracy drops in obesity: Madden 2016 found WHO the most accurate on average in BMI ≥25/≥30 and Henry in BMI ≥40, even though Mifflin was the most precise. During and after weight loss in people with excess weight, Harris-Benedict showed the smallest bias, but prediction intervals were wide. For severe obesity, see "Overweight and obesity: equation choice".
**Sources:** [S161], [S163], [S267], [S268], [S819]

### Overweight and obesity: equation choice
**Rule:** For clients with BMI 30-40, start with MSJ. For BMI ≥40, also calculate Harris-Benedict (or WHO) and treat the range between them and MSJ as the plausible starting band. Do not switch to an FFM equation (Cunningham, Katch-McArdle) in obesity, especially with a smart-scale FFM. Rely on weight-trend recalibration sooner.
**Evidence:** In BMI 30-39.9 and ≥40, MSJ puts about 75% of predictions within ±10% of measured REE, so about 25% of people are off by more than 10%. No anthropometric equation predicts total energy expenditure accurately or precisely in obesity. In severe obesity (BMI 40-62), a meta-analysis of 20 studies found WHO (-12 kcal/d) and Harris-Benedict (-19 kcal/d) the least biased, while MSJ, Owen, Bernstein and Cunningham tended to underestimate. Overweight or obese former athletes were overestimated by all seven equations tested, including Katch-McArdle and Cunningham (+4.3-14.9%).
**Grade:** moderate
**Applies to:** Healthy adults with overweight or obesity. The severe-obesity meta-analysis covered ages 28-55 and BMI 40-62, and most included studies were at high risk of bias.
**Individual variation / conflicts:** Sources disagree on the best equation: Madden found Mifflin the most precise but WHO and Henry the most accurate on average; Campos favours Harris-Benedict/WHO for bias in BMI ≥40 and notes performance may vary across obesity ranges.
**Sources:** [S268], [S162], [S269]

### Older adults: equations overestimate
**Rule:** For clients over about 65, use MSJ as the start but expect roughly 40% of people to be off by more than 10%, with a tendency to overestimate needs. If a deficit is indicated at all (see "Resistance training during any diet, especially for older adults"), keep it conservative; track weight closely, recalibrate from the trend and watch for unintended loss of lean mass, especially if appetite or muscle mass is low.
**Evidence:** A systematic review of 14 studies in healthy older adults found a prevalent tendency to overestimate REE. MSJ had the least group bias (-0.3%), Harris-Benedict +2.6%, and FAO/WHO/UNU, Fredrix and Müller above 5%. Individual precision was poor: about 70% within ±10% for Harris-Benedict, 65% for Henry and 61% for MSJ. In institutionalised older adults (4 studies, n=332), 79% of equations overestimated at group level and individual accuracy did not exceed 41%; the Lührmann equation performed acceptably.
**Grade:** moderate
**Applies to:** Healthy community-dwelling older adults. The institutionalised data (emerging, 4 observational studies) come from long-term-care residents and may not apply to healthy older lifters.
**Individual variation / conflicts:** MSJ is best at group level and Harris-Benedict best at individual level, so the two metrics disagree. No equation was both accurate and precise.
**Sources:** [S280], [S164]

### Trained clients: Cunningham or ten Haaf
**Rule:** For a client who trains regularly and has a credible FFM measurement (DXA or air-displacement plethysmography), Cunningham is a reasonable alternative to MSJ. With no body composition data, use the weight-based ten Haaf equation: REE (kJ/d) = 49.940 × kg + 2459.053 × m - 34.014 × age + 799.257 × (male = 1) + 122.502; divide by 4.184 for kcal. Expect MSJ to be less accurate in trained people, and recalibrate from the weight trend either way.
**Evidence:** In a meta-analysis of 29 studies (1,430 athletes, including 5 studies of recreational exercisers), ten Haaf was the most precise (80.2% within ±10%) versus 40.7-63.7% for the others: about 54% for Cunningham, 52% for weight-based MSJ and 45% for FFM-based MSJ. Cunningham did not differ significantly from measured RMR on average (ES 0.15, 95% CI -0.26 to 0.57; I² 93%), while MSJ, Owen and FAO/WHO/UNU were significantly biased. In 90 Dutch recreational athletes (about 9 h/week), Cunningham and ten Haaf performed well; Harris-Benedict, WHO, Schofield, Mifflin and Owen were under 50% accurate.
**Grade:** moderate
**Applies to:** Adult athletes and recreational exercisers, mostly young (ten Haaf sample 18-35), Dutch, US and European samples. Gym-goers with ordinary muscle mass are a weaker fit. Do not generalise to older or sedentary adults or to obesity.
**Individual variation / conflicts:** The authors state no single equation is guaranteed to be superior. Heterogeneity was high (I² 80-93%) for all except ten Haaf (I² 0%). Individual studies found Cunningham overestimating by about 10% (male cyclists) and 17% (male rugby league players) and underestimating by about 16% (female elite endurance athletes); it significantly overestimated (ES 0.97) in studies following best-practice test preparation. In 187 collegiate athletes, all 10 equations including Cunningham underestimated RMR (best RMSE about 404 kcal in men). Results depend on sex, training level and measurement protocol.
**Sources:** [S165], [S270], [S271]

### Very muscular or physique-trained clients
**Rule:** For unusually muscular clients, expect standard equations to underestimate. Start from Cunningham or ten Haaf (FFM-based) when FFM is measured, or from the Tinsley equations (RMR = 24.8 × BW + 10, or RMR = 25.9 × FFM + 284 kcal/d), and be ready to correct upward from the weight trend. During a lean-gain phase, do not re-run an equation to track RMR changes; use intake versus weight trend instead.
**Evidence:** In 27 muscular physique athletes (men about 12.5% body fat, BMI about 29), nearly all weight- and DXA-FFM-based equations underestimated RMR; only FFM-based ten Haaf and Cunningham gave potentially acceptable estimates. The Tinsley equations were checked only by leave-one-out cross-validation. In 20 resistance-trained men doing 6 weeks of training plus a surplus, measured RMR rose 165 kcal/d and every equation underestimated the change by 75-155 kcal/d.
**Grade:** emerging
**Applies to:** Resistance-trained or physique-athlete men and women in small US samples from one lab. Use only for advanced, very muscular gym-goers.
**Individual variation / conflicts:** Small samples and no external validation of the new equations. Fields 2023 found even FFM equations underestimating in collegiate athletes.
**Sources:** [S272], [S273]

### Katch-McArdle
**Rule:** Use Katch-McArdle only as an alternative estimate when FFM is credibly measured, and never present it as more accurate than MSJ for ordinary adults. If an app's Katch-McArdle and MSJ results differ by more than 10%, take the midpoint and let the weight trend decide. Do not use equation-based or BIA-device RMR changes to diagnose "metabolic adaptation".
**Evidence:** Katch-McArdle is RMR = 370 + 21.6 × lean body mass (kg). Validation against calorimetry is sparse, and it is not in the 2023 athlete meta-analysis. In 400 adults in Trinidad and Tobago it was among the most accurate body-composition equations; in 56 overweight or obese former athletes it overestimated RMR by 70-300 kcal/d (4.3-14.9%), like all six other equations. In a 16-week weight-loss trial (n=131), Katch-McArdle and BIA-device RMR estimates gave opposite conclusions about metabolic adaptation, and neither was measured RMR.
**Grade:** emerging
**Applies to:** Healthy adults, in small population-specific samples (Caribbean adults, Portuguese former athletes); the Chinese weight-loss trial had no calorimetry reference.
**Individual variation / conflicts:** Its accuracy depends entirely on the FFM input. No systematic review evaluates it on its own, and results conflict between populations.
**Sources:** [S274], [S275], [S269], [S165]

### FFM versus body-weight equations for atypical body composition
**Rule:** When a client's body composition is atypical for their weight (very muscular, or high fat at normal BMI) and FFM comes from a decent method, cross-check MSJ with an FFM equation. If they disagree, start from the FFM estimate, then recalibrate from the weight trend.
**Evidence:** In 50 adults from sedentary to ultra-endurance (DXA), FFM equations were more accurate than body-mass equations overall, with the Pontzer FFM equation most accurate; body-mass equations were less accurate in women and were affected by activity and body composition. In 104 adults (mean BMI about 26), FFM explained 69% (BIA) to 75% (DXA) of REE variance versus 46% for body weight.
**Grade:** emerging
**Applies to:** Healthy adults of mixed activity (US, n=50) and German adults aged about 35-37 (n=104). Small, cross-sectional samples.
**Individual variation / conflicts:** FFM equations were slightly less accurate in men. Published FFM equations differ widely, reflecting population and investigator specificity, so no single FFM equation fits everyone.
**Sources:** [S276], [S277]

### Body-fat measurement error carries into RMR
**Rule:** Feed an FFM equation only with body fat from DXA, BodPod, research-grade or octapolar BIA, or competent skinfolds. If the only number comes from a foot-to-foot or hand-held smart scale, use MSJ instead. Never re-estimate RMR from week-to-week smart-scale body-fat changes. For tracking, use the same device under standardised conditions.
**Evidence:** With lab methods, FFM-predicted REE barely changes with technique: in 104 adults, skinfold, BIA, DXA, ADP and D2O-based estimates did not differ from a 4-compartment reference (slopes about 24-26 kcal per kg FFM). Spectral BIA versus DXA in 30 trained men gave a mean RMR bias of -35 kcal/d. Across 15 BIA devices (14 consumer-grade) in 73 adults, group-mean error ranged from -3.5% to +11.7% body fat (SEE 3.1-7.5%). Illustrative arithmetic: a 5-point body-fat error in an 80 kg person is 4 kg FFM, about 95-105 kcal/d; an 11.7-point error is about 225-240 kcal/d. Longitudinal error is smaller (group error -0.4% to +1.3%, SEE 1.7-2.6%).
**Grade:** moderate
**Applies to:** Healthy adults aged 19-50 (device study), adults with mean BMI about 26 (n=104), and young lean trained men (n=30). The kcal figures are arithmetic from published slopes, not measured outcomes.
**Individual variation / conflicts:** Error varies widely by device and individual, and group means hide larger individual errors. The good BIA-versus-DXA agreement came from a spectral device in lean young men and does not apply to cheap scales or obesity. Evidence is from single validation studies.
**Sources:** [S278], [S277], [S279]

### Activity multipliers (PAL)
**Rule:** Multiply estimated RMR by a PAL: about 1.4-1.5 (up to 1.6) for desk workers with little exercise or a few short sessions a week; about 1.6-1.75 for desk workers who train most days for about 1 hour; 1.7-1.9 only for physically active jobs or daily moderate-vigorous exercise plus high daily movement. Never use 1.2 for ambulatory adults, do not go above about 2.0 for recreational gym-goers, and never above 2.4. Treat the result as a first guess to correct after 2-4 weeks of weight data.
**Evidence:** FAO/WHO/UNU defines PAL (24-h TEE/BMR) 1.40-1.69 as sedentary or light, 1.70-1.99 as active or moderately active, and 2.00-2.40 as vigorous; values above 2.40 are hard to sustain. A mostly sedentary Western lifestyle sits around 1.55-1.65, and about 1 h/day of moderate-to-vigorous exercise raises a sedentary worker from about 1.55 to about 1.75. The consultation judged 1.21 too low even for emergency relief and suggested 1.40 instead. Doubly labelled water puts the maximum habitual PAL at about 2.00-2.40. The app "sedentary" value of 1.2 sits below the range for free-living adults.
**Grade:** moderate
**Applies to:** Healthy adults. FAO PAL is defined against BMR and DLW PAL against REE, while apps multiply an RMR estimate, so factors are approximately comparable. Very inactive, ill or dependent people can fall below 1.40.
**Individual variation / conflicts:** The bands are population categories, and placing an individual in one is subjective. The 1.375/1.55/1.725 app steps are convention, not validated against DLW, and the 1.4-1.5 floor is an inference from the guideline. Combined with ±10% RMR error, TDEE can be off by several hundred kcal/day.
**Sources:** [S166], [S281]

### Self-reported activity is noisy
**Rule:** Do not apply a blanket "subtract one activity level" correction. Distrust self-reported minutes of moderate-to-vigorous exercise, ask about occupation and daily steps, choose the lower plausible multiplier when unsure, and let the weight trend correct the individual error.
**Evidence:** A review of 187 studies found self-reported activity both higher and lower than measured, with correlations from -0.71 to 0.96 and no clear pattern. A review of 20 questionnaire-versus-DLW publications found neither over- nor under-reporting more common at group level. In 385 US adults, NHANES questionnaire activity energy matched DLW at group level (3.4 vs 3.6 MJ/d), but individual error was large and self-reported MVPA was inflated about 4.5-fold (36 vs 8 min/d).
**Grade:** moderate
**Applies to:** General adult populations using questionnaires. App drop-down self-categorisation has not been validated against DLW.
**Individual variation / conflicts:** MVPA minutes are over-reported, but total activity energy shows no consistent bias; direction differed by method, activity level and gender. Error is individual and unpredictable.
**Sources:** [S284], [S285], [S286]

### PAL-free starting models
**Rule:** When a client cannot describe their activity reliably, a PAL-free DLW-derived model (the Pennington energy requirement calculator) is a defensible start instead of RMR × multiplier. Follow it with at least 4 weeks of weight-trend recalibration.
**Evidence:** Models built from DLW-measured TEE in 119 adults predicted free-living requirements without activity input (adjusted R² 0.65 from age, height and weight; 0.74 adding body composition and RMR).
**Grade:** emerging
**Applies to:** US adults in the Pennington database and independent validation sets. About a third of TEE variance remains unexplained individually.
**Individual variation / conflicts:** Validation differed by study and sex. No trial shows it beats RMR × PAL for coaching outcomes.
**Sources:** [S294]

### Exercise calories do not add linearly
**Rule:** When a client adds cardio, do not move them up a full activity tier or add the full calories a watch reports. On average only part of the calories burned in exercise show up as weight loss because of compensation, and how much varies a lot between people, so do not eat back more than about half of the estimated exercise calories; the weight trend is the real calibration. Resistance training seems less compensated, but still verify. Encourage keeping non-exercise steps up during a deficit.
**Evidence:** Across aerobic exercise interventions, TDEE rose by only about 30% of the increase predicted by additive models; compensation appeared smaller with resistance training and larger when aerobic exercise was combined with dieting. In a 24-week aerobic trial (n=29 adults with obesity, DLW), 48% compensated by an average -308 ± 158 kcal/d, without measurable adaptation in resting or sleeping expenditure.
**Grade:** moderate
**Applies to:** Mostly adults in supervised aerobic programmes (Flanagan: mean age about 48, BMI about 34, low fitness). Resistance-training data are thinner, and generalising to lean trained gym-goers is uncertain.
**Individual variation / conflicts:** The constrained versus additive debate is ongoing. About half of people compensate and half do not (related to baseline TDEE, r=-0.50). Mechanisms disagree: some reviews report falls in REE and non-exercise activity, especially in a deficit, while Flanagan found no resting adaptation.
**Sources:** [S282], [S283], [S281]

### Recalibrate TDEE from the weight trend
**Rule:** Start from equation × conservative multiplier. Weigh under the same conditions and log intake consistently. Daily weighing averaged weekly gives the cleanest trend and is what the trend tool prefers; weekly weighing is acceptable; weighing is never required, and there are no weigh-ins at all when the eating-disorder rule applies (see "Eating-disorder screening: brief questions as a prompt"). After 2 weeks, check only the direction. After 4 or more weeks, compute observed TDEE = mean logged intake - (trend weight change × energy density ÷ days), and replace the equation estimate with it. Adjust intake in steps of about 100-200 kcal/d and re-check after another 2-4 weeks. Treat logged calories as "logged-calorie units" and keep the logging method constant.
**Evidence:** Simulations show daily weighing for more than 28 days is needed to estimate an individual's intake change with a 95% CI under 300 kcal/d, largely regardless of initial body composition or activity. Validated against DLW/DXA in 140 CALERIE participants over 2 years, a weight-only model was within 40 kcal/d at group level, with individual RMSD 215 kcal/d (most within 132 kcal/d). Self-reported intake is mostly under-reported against DLW (59 studies, 6,298 adults).
**Grade:** moderate
**Applies to:** Adults in weight-loss or maintenance phases (CALERIE caloric-restriction participants; simulated adults for precision). The precision figures assume daily weighing; with weekly weighing, expect a noisier estimate and allow more weeks before adjusting.
**Individual variation / conflicts:** Below about 4 weeks the CI exceeds 300 kcal/d, so 2-week adjustments are noisy. The validated method is weight-only; the logged-intake calculation in this rule is not validated and assumes a constant logging bias, which varies widely between people. Commercial adaptive-TDEE apps have no peer-reviewed validation in the sources reviewed. The weight trend does not separate fat from fluid, glycogen or muscle, so beginners starting resistance training and women with cycle-related water shifts should also use waist and photos. The 100-200 kcal step size is a practical heuristic.
**Sources:** [S287], [S288], [S289]

### Read the scale with weekly averages
**Rule:** Never adjust calories from one or two weigh-ins. Daily weighing is optional; weekly is acceptable. Weigh under standard conditions (morning, after the toilet, before eating), use 7-day rolling averages (when weighing daily) or same-weekday comparisons, and compare weekly means across 2-4 weeks. Treat a Monday rise of up to about 0.5% of body weight as noise, and expect transient jumps after holidays or high-salt or high-carbohydrate days.
**Evidence:** In 1,421 NoHoW participants, within-week fluctuation was 0.35% of body weight (weekend gain, weekday loss), and Christmas added a mean 1.35% not fully compensated in the following months (n=1,062). In 80 daily-weighing adults, weight peaked Sunday-Monday and fell through the week, most clearly in people who lost or maintained weight.
**Grade:** emerging
**Applies to:** Adults using scales. NoHoW: European adults who had lost ≥5% of weight from BMI ≥25; Orsama: adults with BMI 20-33.5, age 25-62. The 0.5% threshold extrapolates from group means.
**Individual variation / conflicts:** The rhythm differed by gender, country, BMI and age. Fluid shifts from creatine, high-carbohydrate days, sodium or the menstrual cycle can hide fat change for 1-2 weeks; cycle-related shifts are not covered by these sources.
**Sources:** [S290], [S291]

## Weight change, deficits and surpluses

### Expected weight change: the 3500 kcal rule is wrong
**Rule:** Do not promise linear loss from a fixed deficit (for example, 500 kcal/day = 0.45 kg/week forever). Tell clients that loss slows as weight falls, even with perfect adherence. Forecast with a dynamic model (NIH Body Weight Planner or the Pennington tools) or simply set that expectation, and re-estimate intake after every ~5% of body-weight change or whenever the trend stalls for 3-4 weeks. When recalibrating, use an energy density well below 7700 kcal/kg in the early weeks (water and glycogen) and for lean clients. At a plateau, recalculate TDEE from the current trend instead of assuming "metabolic damage". Use the 3500 kcal rule only for rough short-term arithmetic.
**Evidence:** In a validated dynamic model, each permanent 100 kJ/day (about 24 kcal/day) change in intake eventually changes weight by about 1 kg (roughly 10 kcal/day per lb); about half the change takes around 1 year and 95% around 3 years. In seven supervised weight-loss experiments, the static rule overestimated actual loss. Lost tissue energy depends on body fat (about 39.5 MJ/kg for fat vs 7.6 MJ/kg for lean); the 3500 kcal/lb rule only approximates this when initial body fat is above about 30 kg, and leaner people need a smaller cumulative deficit per kg but lose more lean tissue.
**Grade:** moderate
**Applies to:** Adults losing weight, mainly with overweight or obesity. Predictions are model-based and validated at group level.
**Individual variation / conflicts:** People with more body fat lose more for the same intake change and take longer to plateau. Individual trajectories deviate because of adherence, water shifts and adaptive thermogenesis.
**Sources:** [S159], [S160], [S292], [S293]

### Deficit size for weight loss (overweight and obesity)
**Rule:** For adults with overweight or obesity, set a deficit of about 500-750 kcal/day (up to about 30% below estimated TDEE), individualised from estimated TDEE rather than fixed kcal ranges. Frame the initial goal as 5-10% of body weight over about 6 months, and tell the client that even 3-5% sustained improves health markers. For lean clients, use a smaller deficit or a percent-of-body-weight rate (see "Rate of loss for lean, trained clients").
**Evidence:** The 2013 AHA/ACC/TOS guideline recommends 1200-1500 kcal/day for women and 1500-1800 kcal/day for men, or a 500 or 750 kcal/day deficit (Grade A); its review also supports a 30% deficit. Sustained loss of 3-5% gives clinically meaningful benefits, with more benefit from more loss (Grade A). Initial goal: 5-10% of baseline weight within 6 months.
**Grade:** strong
**Applies to:** Adults with overweight or obesity in clinical and lifestyle programmes (US). Not designed for lean, trained people trying to keep muscle.
**Individual variation / conflicts:** The fixed kcal ranges can be too aggressive for small, older or very active people and too generous for large people; the guideline notes they are usually adjusted. This file's minimum-intake rule (never below about 1,200 kcal/day for women or 1,500 kcal/day for men without clinical supervision) takes precedence, and GLP-1 users get no coach-imposed deficit (see "GLP-1 users: protein, training and red flags"). The guideline gives no weekly loss rate in kg; weekly paces elsewhere in this file are conventions or come from other sources. The guideline is from 2013 and predates pharmacotherapy-era guidance.
**Sources:** [S167]

### Deficit size when keeping or building muscle
**Rule:** For clients who want to keep or build muscle while losing fat, keep the deficit at or below about 500 kcal/day, with high protein and resistance training throughout. Tell them strength usually keeps rising in a moderate deficit even when muscle gain stalls. Avoid long, aggressive deficits for anyone whose main goal is muscle.
**Evidence:** In a meta-analysis of RCTs (≥3 weeks of resistance training), training in a deficit impaired lean-mass gains versus no deficit (ES -0.57, p=0.02), but strength gains were similar (ES -0.31, p=0.28). A matched secondary analysis agreed (lean mass ES -0.11 vs +0.20). Meta-regression estimated that about 500 kcal/day prevented lean-mass gains. In lean resistance-trained athletes, the groups that kept FFM were mostly those with the most body fat, the smallest restriction or a novel training stimulus.
**Grade:** moderate
**Applies to:** Adults doing resistance training in RCTs of ≥3 weeks; training status and body composition were not stated in the abstract. Not specific to elite athletes.
**Individual variation / conflicts:** The 500 kcal/day threshold is an average from heterogeneous studies, not an individual cut-off. Beginners and people with more body fat often gain lean mass in a deficit, and lean people may need smaller deficits (extrapolation).
**Sources:** [S169], [S190]

### Prefer gradual over rapid loss
**Rule:** Prefer gradual over rapid loss for better fat loss and a smaller RMR decline. Do not tell clients that faster dieting will "burn their muscle": in this evidence the FFM difference was not significant. Resistance training and adequate protein matter more for lean mass than speed alone.
**Evidence:** With equal total weight loss in adults with overweight or obesity, gradual loss led to more fat-mass loss (-1.0 kg, 95% CI -1.70 to -0.29), a larger fall in body-fat % (-0.83%) and significantly better preserved RMR. FFM loss and waist/hip measures did not differ significantly.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity (studies up to October 2019). Evidence in lean or trained people is sparser.
**Individual variation / conflicts:** The published RMR effect size and its confidence interval are internally inconsistent (the interval does not bracket the point estimate), so no RMR magnitude is given here. The meta-analysis does not define a rate. In lean, trained people, speed may matter more for lean mass.
**Sources:** [S168]

### Rate of loss for lean, trained clients
**Rule:** For lean, trained clients who want to keep muscle, aim for about 0.5-1% of body weight per week, moving toward the slower end as they get leaner. Clients with more fat to lose can go toward the faster end.
**Evidence:** An evidence-based review of natural bodybuilding contest preparation recommends calorie intake that drops body weight by about 0.5-1% per week to maximise muscle retention.
**Grade:** emerging
**Applies to:** Lean, mostly young male competitors. Generalising to ordinary gym-goers is an extrapolation.
**Individual variation / conflicts:** A narrative review built on few trials, not a position stand. In people with overweight, rate of loss made no significant FFM difference (see "Prefer gradual over rapid loss").
**Sources:** [S170]

### Adaptive thermogenesis is real but modest
**Rule:** Tell clients metabolism does adapt, but modestly (typically under about 100 kcal/day at rest) and partly reversibly. When fat loss stalls, look first at intake creep, lower NEAT and step count, and the smaller body size, not "metabolic damage". Use maintenance phases at the new weight to let the adaptation fade.
**Evidence:** Well-designed studies report small or non-significant adaptive thermogenesis that shrinks once energy balance is restored. In 71 adults with obesity losing ~14 kg on 1000 kcal/day, RMR was 92 ± 110 kcal/day below predicted at week 9, 38 ± 124 kcal/day after 4 weeks of stabilisation, and not different at 1 year (-7 ± 129 kcal/day). It did not predict regain.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity. Data in lean, trained people are scarcer, and adaptation may be larger in very lean states.
**Individual variation / conflicts:** How to quantify it is disputed (Martins 2020 drew critical commentary), and between-person variation is large (SD ~110-130 kcal/d). Larger adaptations in extreme-loss settings are not covered.
**Sources:** [S171], [S172]

### Resistance training during any diet, especially for older adults
**Rule:** Any client in a deficit should do resistance training at least 2-3 times a week throughout the diet; older adults start at 2 days a week and progress to 3 if recovery allows. Do not set a deficit for older adults (about 65+) unless they have obesity with a weight-related health problem; then use a modest deficit plus resistance training, never diet-only weight loss, with protein as in "Older adults: protein targets" (at least 1.0-1.2 g/kg/day, 1.2-1.6 g/kg/day when lifting). Monitor strength and function, not just scale weight.
**Evidence:** In obese older adults (6 RCTs, resistance training 3×/week for 12-24 weeks), adding training to caloric restriction prevented 93.5% of the lean-mass loss caused by restriction alone (0.82 kg, 95% CI 0.36 to 1.27), with no difference in fat or body-mass loss. In 20 RCTs in adults over 50, higher-protein diets (≥25% of energy or ≥1.0 g/kg/day) kept more lean mass and lost more fat during weight loss. ESPEN's 2022 geriatric guideline says dietary restrictions should generally be avoided and weight-reducing diets considered only in obese older persons with weight-related health problems, combined with physical exercise.
**Grade:** moderate
**Applies to:** Adults over 50 with overweight or obesity; the training analysis covers obese older adults only, in supervised RCTs. The direction likely applies to younger adults, but the magnitude is specific.
**Individual variation / conflicts:** Only 6 training RCTs, so the magnitude is imprecise. Trial diets were mostly about 15% protein, so the training effect was shown without high protein. Neither meta-analysis compares training and protein directly. The 2×/week starting point is an extrapolation from 3×/week trials and matches the strength file's progression for older adults. Check kidney function and comorbidities in this group.
**Sources:** [S173], [S195], [S668]

### Surplus size for muscle gain
**Rule:** For muscle gain, use a modest surplus (about 5-20% above maintenance, not above about 20%) and aim for about 0.25-0.5% of body weight per week. Beginners and returning lifters can sit near the top, advanced lifters near the bottom; start at the lower end, because prescribed surpluses tend to drift upward. Expect a planned small surplus to drift upward, so track weekly average weight rather than trusting the kcal target. If waist or skinfolds rise faster than strength and measurements improve, reduce the surplus.
**Evidence:** No validated sweet spot exists. Narrative-review guidance for natural bodybuilders is a ~10-20% surplus targeting ~0.25-0.5% of body weight per week for novice and intermediate lifters, less for advanced. In an 8-week RCT in trained lifters (n=17 completers), groups prescribed 5% and 15% surpluses actually ate about +490 and +720 kcal/day and both gained about 3.3 kg (maintenance +0.4 kg). Weight gain predicted skinfold gain (R²=0.49) but not squat 1RM or muscle thickness; bench 1RM rose more with the higher surplus. The authors recommend 5-20% (0.25-0.5% BW/week), slower for advanced trainees.
**Grade:** emerging
**Applies to:** Trained, mostly young men (2 women of 17, mean age about 27). Generalising to beginners, women and older adults is extrapolation; the RCT authors suggest less-trained people may benefit from larger surpluses.
**Individual variation / conflicts:** The two sources give overlapping ranges (10-20% in the narrative review, 5-20% from the RCT authors). Recommendations are expert opinion; the only trial is small, underpowered and missed its prescribed surpluses. One other study (Smith et al.) found weight gain predicted FFM gain. The ideal surplus likely depends on training age, body fat, genetics and programme.
**Sources:** [S174], [S175], [S176]

### Body recomposition
**Rule:** For beginners, returning lifters and clients with higher body fat, recomposition is reasonable: eat around maintenance or a small deficit (clearly below 500 kcal/day), train progressively and keep protein high. Track waist, photos and strength rather than scale weight alone. For lean, experienced lifters wanting maximal muscle, expect slow recomposition and consider a modest surplus phase.
**Evidence:** Gaining muscle while losing fat is documented in untrained and overweight people and, per a narrative review, in trained people; progressive resistance training and good nutrition are the drivers. In the deficit meta-analysis, strength gains were similar with or without a deficit (ES -0.31) while lean-mass gains were impaired (ES -0.57), with about 500 kcal/day predicted to stop them.
**Grade:** emerging
**Applies to:** Untrained, detrained and overweight adults most clearly; trained people per a narrative review. Older adults are not specifically addressed.
**Individual variation / conflicts:** The trained-population evidence is narrative, and the threshold comes from one meta-regression. Body-composition measurement error (BIA, DXA hydration) can create or hide apparent recomposition. The effect shrinks with training status and leanness.
**Sources:** [S177], [S169]

### Diet breaks
**Rule:** Offer diet breaks (1-2 weeks at estimated maintenance after every 2-3 weeks of deficit, the protocols tested) as an adherence and hunger tool, especially for long diets or hungry clients. Do not sell them as a way to speed fat loss or protect muscle in trained people, and make clear they lengthen the total time to goal. Longer deficit blocks between breaks are untested.
**Evidence:** A 2025 meta-analysis (12 RCTs, 881 participants) found similar body-mass, fat-mass and body-fat changes with breaks versus continuous restriction; RMR fell significantly only with continuous restriction, more clearly in overweight than trained people. In trained adults (ICECAP, n=61), 1-week breaks after each 3-week block gave similar fat loss, FFM, REE and strength, with lower hunger. In men with obesity (MATADOR), 2-week on/off blocks gave more weight loss (14.1 vs 9.1 kg) and a smaller adjusted REE drop (-360 vs -749 kJ/d), over 30 vs 16 weeks.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity and resistance-trained adults (ICECAP mean age 28.7, 32 women of 61). MATADOR covers men with obesity only (mean age about 40).
**Individual variation / conflicts:** MATADOR and ICECAP disagree on efficiency. The pooled RMR effect was not in the abstract and is likely small, and the meta-analysis has a correction that could not be checked. Claims that breaks "reset metabolism" outrun the evidence.
**Sources:** [S178], [S179], [S180]

### Refeeds and cheat meals
**Rule:** Do not prescribe refeeds or cheat meals for metabolic reasons. If a client wants a planned higher-calorie day for psychological relief, fit it into the weekly energy budget and watch for loss-of-control eating.
**Evidence:** A 2025 scoping review found only 4 physiology studies (125 participants, 4-6 weeks): compatible with weight loss, inconclusive on reducing metabolic adaptation, mixed on lean mass. Unplanned episodes may resemble disordered eating.
**Grade:** emerging
**Applies to:** Small, short studies in overweight women, healthy adults and a few male bodybuilders.
**Individual variation / conflicts:** Claims that refeeds "boost leptin or metabolism" are unsupported. Psychological effects vary, and some people may be harmed.
**Sources:** [S181]

## Protein

### Baseline protein requirement
**Rule:** Treat 0.83 g/kg/day as the reference floor for any adult, and flag habitual intakes below it, especially below 0.66 g/kg/day. For clients who lift, aim higher (see "Daily protein target for people who lift"). Explain that the official reference intake and sports targets answer different questions and do not contradict each other.
**Evidence:** EFSA's Population Reference Intake is 0.83 g/kg/day, from an average requirement of 0.66 g/kg/day (nitrogen-balance meta-analysis) plus the 97.5th percentile. It is the same for both sexes, all weights and all adult ages; EFSA's 2017 summary report repeats these values, treats older adults' requirement as equal to that of adults and considers twice the PRI safe. AESAN (2019) adopts EFSA's values for Spain. It is an adequacy value for maintenance, not a muscle-gain target.
**Grade:** strong
**Applies to:** Healthy European adults of all ages, including Spain.
**Individual variation / conflicts:** EFSA found data insufficient to set a separate value for older adults and noted several studies suggest they may need more; geriatric societies recommend more (see "Older adults: protein targets").
**Sources:** [S795], [S183], [S184]

### Daily protein target for people who lift
**Rule:** Default to about 1.6 g/kg/day, the estimate where extra protein stops adding measurable fat-free mass, with 1.4-2.2 g/kg/day as the acceptable range. Go toward 2.0-2.2 in a deficit or for a safety margin. Older adults, GLP-1 users and anyone with kidney disease follow their own rules ("Older adults: protein targets", "GLP-1 users: protein, training and red flags", "Chronic kidney disease"). Do not push above about 2.2 g/kg/day to build muscle at maintenance or in a surplus. Use body weight for lean or normal-weight clients; for clients with obesity, base the target on fat-free mass or goal weight (a practical heuristic).
**Evidence:** The ISSN recommends 1.4-2.0 g/kg/day for most exercising people. Morton 2018 (49 RCTs, 1,863 participants, ≥6 weeks of resistance training) found FFM gains stopped rising at 1.62 g/kg/day (95% CI 1.03-2.20) in a subset breakpoint analysis (not significant, p=0.079, unadjusted); the authors suggest ~2.2 g/kg/day to be sure. Nunes 2022 (74 RCTs, healthy non-obese adults) found a lean-mass benefit under 65 with ≥1.6 g/kg/day during resistance exercise.
**Grade:** moderate
**Applies to:** Healthy adults doing structured resistance training, including beginners. Morton's sample mean age 35 ± 20; only 10 of 49 studies in trained people; evidence in women and people with obesity is thinner.
**Individual variation / conflicts:** The breakpoint is imprecise (wide CI, non-significant), which is why this rule is graded moderate, and individual plateaus vary. Tagawa 2021 reports a smaller continued benefit up to 3.5 g/kg/d rather than a hard plateau. Morton's senior author and several Nunes authors declare dairy or nutrition-industry ties.
**Sources:** [S185], [S186], [S187]

### Keep the protein effect in proportion
**Rule:** Present protein as support for training, not the main driver. The biggest return comes from raising low intakes (below 1.2-1.3 g/kg) to target. Past about 1.6 g/kg, adherence, training progression and total energy matter more than extra grams. Do not sell protein powders as the key to results.
**Evidence:** Protein supplementation during ≥6 weeks of resistance training added +0.30 kg FFM (95% CI 0.09-0.52) and +2.49 kg 1RM (Morton). Nunes found a small lean-mass effect (SMD 0.22) and only a marginal effect on physical function. In Tagawa's dose-response meta-analysis (105 articles, n=5,402), each +0.1 g/kg/day added +0.39 kg lean mass below 1.3 g/kg/day but only +0.12 kg above it.
**Grade:** strong
**Applies to:** Adults in RCTs of weeks to months. Long-term (years) effects are not measured directly.
**Individual variation / conflicts:** Tagawa (5 of 7 authors employed by Meiji) finds a small continued benefit; Morton finds a plateau around 1.6. Both agree the benefit is small. Several authors report industry funding.
**Sources:** [S186], [S188], [S187]

### Who benefits most from extra protein
**Rule:** Prioritise the higher protein targets for clients who train consistently or are dieting. For true beginners, the extra benefit above an adequate intake is small and uncertain, so put training first and treat ~1.4-1.6 g/kg as sensible rather than mandatory. For a sedentary client not in a deficit, reaching the reference intake and starting training matters far more than high protein. Older clients still benefit but need training plus a higher daily intake.
**Evidence:** In Morton's meta-regression the FFM benefit was larger in trained people (+0.75 kg) and smaller with age (-0.01 kg per year); subgroups showed 1.05 kg in trained versus 0.15 kg (not significant) in untrained participants. Hudson 2020 (18 RCTs) found intakes above the RDA helped lean mass during energy restriction (+0.36 kg, 14 comparisons) and resistance training (+0.77 kg, 3 comparisons), but not under non-stressed conditions (+0.08 kg, -0.59 to 0.75).
**Grade:** moderate
**Applies to:** Healthy adults. Trained-versus-untrained and age comparisons are between-study, not head-to-head; Hudson's training subgroup is tiny.
**Individual variation / conflicts:** Meta-regression covariates can be confounded. The smaller effect with age reflects weaker muscle response, which argues for more protein in older adults, not less.
**Sources:** [S186], [S189]

### Protein during fat loss
**Rule:** During fat loss, keep protein at about 1.8-2.2 g/kg/day for ordinary lifters and keep resistance training going. Reserve about 2.3-3.1 g/kg of fat-free mass for lean, trained clients in aggressive deficits. For clients with more body fat, calculate from fat-free mass or goal weight; for overweight beginners on a modest deficit, ~1.6-2.0 g/kg plus training is probably enough. This rule does not apply to GLP-1 or tirzepatide users (see "GLP-1 users: protein, training and red flags": 1.2-1.6 g/kg/day unless the clinician says otherwise) or to anyone with kidney disease (see "Chronic kidney disease").
**Evidence:** Above-RDA intakes reduced lean-mass loss during energy restriction by 0.36 kg (95% CI 0.06-0.67; Hudson). The ISSN states 2.3-3.1 g/kg/day "may be needed" for trained people in a deficit, a figure from Helms 2014 (6 studies in lean trained adults, expressed per kg FFM). In a 4-week RCT of young men on a ~40% deficit with resistance training plus HIIT 6 days/week, 2.4 g/kg gave more lean-mass gain (+1.2 vs +0.1 kg) and fat loss (-4.8 vs -3.5 kg) than 1.2 g/kg.
**Grade:** moderate
**Applies to:** Adults in a deliberate deficit. The highest values come from small samples of lean, mostly male athletes; Longland's trial used an extreme deficit and training load.
**Individual variation / conflicts:** "1 g per lb" or >2.5 g/kg for every dieter outruns the evidence. The 1.8-2.2 g/kg range is an extrapolation between sources, not a tested value; no dose-finding trial in overweight beginners was found.
**Sources:** [S185], [S190], [S191], [S189]

### Older adults: protein targets
**Rule:** For clients over about 65, treat 1.0-1.2 g/kg/day as the minimum; for those who lift, target 1.2-1.6 g/kg/day. Do not push older clients to 2.0-2.2 g/kg/day. Always pair protein with resistance training. Ask about kidney disease before raising protein; with any diagnosed CKD, the nephrologist or renal dietitian sets the target (see "Chronic kidney disease").
**Evidence:** PROT-AGE recommends ≥1.0-1.2 g/kg/day over 65, ≥1.2 for active people, 1.2-1.5 with acute or chronic disease, with limits in severe kidney disease (eGFR <30, not on dialysis). ESPEN recommends ≥1.0-1.2 g/kg/day for healthy older people, 1.2-1.5 if malnourished or ill, plus daily exercise. Nunes 2022 found a significant lean-mass benefit in people ≥65 eating 1.2-1.59 g/kg/day with resistance exercise.
**Grade:** moderate
**Applies to:** Adults over 65; Nunes included only healthy non-obese adults. Values for ages 50-65 are extrapolated.
**Individual variation / conflicts:** EFSA keeps 0.83 g/kg for older adults. The protein scoping review written for NNR 2023 reports that prospective cohort studies suggest up to 1.2-1.5 g/kg/day (about 15-20 E%) as an optimal intake for older adults, and that several expert groups suggest 1.0-1.2 g/kg/day for healthy older adults; this is mostly observational, and the same review cites trials and a Dutch systematic review finding insufficient evidence that more protein brings health benefits in older adults already eating at least 0.8 g/kg/day. It informed NNR 2023 but is not its formal recommendation text. The added lean mass is small (SMD 0.22).
**Sources:** [S192], [S193], [S187], [S194], [S820]

### Protein distribution across meals
**Rule:** Use per-meal protein (about 0.3-0.4 g/kg, about 25-40 g for most adults, across 3-5 meals) as a practical way to reach the daily total, not as a separate requirement. If a client can only manage 2-3 meals, focus on the daily total.
**Evidence:** The ISSN suggests 0.25 g/kg or 20-40 g of high-quality protein per serving (~700-3000 mg leucine) every 3-4 hours. A narrative review proposes 0.4 g/kg per meal over at least 4 meals (up to 0.55 g/kg for 2.2 g/kg/day). These figures rest mainly on acute muscle-protein-synthesis studies.
**Grade:** moderate
**Applies to:** Adults who lift; per-meal data mostly from young adults. Older adults may need larger doses per meal.
**Individual variation / conflicts:** Long-term evidence does not show that even distribution beats uneven distribution when daily totals match: a systematic review (15 studies, adults 20-85) found even distribution linked to more muscle mass in only 3 of 7 studies (observational), to strength in 2 of 7 and to protein synthesis in 1 of 6; in two 16-week RCTs during weight loss with adequate total protein (41 adults lifting on 90 g/day, 30/30/30 g vs 10/20/60 g; 43 women, even vs evening-skewed), distribution made no difference to body composition. Newer tracer work also questions the per-meal ceiling (see next rule). Do not promise extra lean mass from an even spread.
**Sources:** [S185], [S196], [S799], [S800], [S801]

### Myth: only 20-30 g of protein per meal can be used
**Rule:** Do not tell clients that protein above 25-30 g per meal is wasted. Large protein meals (for example with intermittent fasting or two meals a day) are acceptable if the daily total is met. Spreading intake remains a sensible default.
**Evidence:** Larger doses raise amino-acid oxidation but are still partly used for tissue building. In a tracer study, 100 g of protein after exercise produced a larger and longer (>12 h) anabolic response than 25 g, with negligible effect on oxidation.
**Grade:** emerging
**Applies to:** Healthy young men after whole-body resistance exercise; a single acute study. The authors say it may not extrapolate to women or older adults.
**Individual variation / conflicts:** Conflicts with the earlier view that synthesis maxes out at ~20-25 g per meal. Whether bigger doses produce more muscle over months is untested. One co-author is employed by FrieslandCampina.
**Sources:** [S197], [S196]

### Protein timing and the "anabolic window"
**Rule:** Do not require a protein shake straight after training. Make sure the daily total is met and a protein-containing meal falls within a few hours before or after the session, as convenient.
**Evidence:** A meta-regression of 20-23 RCTs found no significant effect of protein timing on strength or hypertrophy once covariates were controlled; total protein was the strongest predictor. The ISSN says timing is mostly about tolerance and that exercise's anabolic effect lasts at least 24 h.
**Grade:** moderate
**Applies to:** Healthy adults who resistance train, mostly young.
**Individual variation / conflicts:** Older adults and people training fasted early in the morning may benefit more from protein soon after training; plausible but not settled.
**Sources:** [S198], [S185]

### Upper intake and kidney health
**Rule:** Intakes up to about 2.2 g/kg/day are reasonable for healthy lifters, with no need to frighten clients about their kidneys. Do not push above about 2.2-2.5 g/kg/day without a reason, because long-term safety data beyond that are thin. Screen for CKD, diabetes with kidney involvement or a history of kidney stones, and refer those clients before raising protein.
**Evidence:** EFSA found data insufficient to set an upper level and considers intakes up to twice the reference intake (~1.7 g/kg/day) safe. In 28 RCTs (n=1,358), high-protein diets (≥1.5 g/kg, ≥20% of energy or ≥100 g/day) did not change GFR differently from normal intakes in adults without kidney disease (SMD 0.11, 95% CI -0.05 to 0.27). In 14 trained men over 1 year, ~2.5-3.3 g/kg/day showed no harmful effects on lipids, liver or kidney markers.
**Grade:** moderate
**Applies to:** Healthy adults without kidney disease. Trials were mostly months long; the >3 g/kg data come from 14 young trained men.
**Individual variation / conflicts:** EFSA's ~1.7 g/kg is below common sports targets, which reflects a data gap, not proof of harm. People with existing CKD may need to limit protein (see "Chronic kidney disease").
**Sources:** [S199], [S200], [S201], [S192]

### Plant versus animal protein
**Rule:** Vegetarian and vegan clients can reach the same goals. Aim for at least the default protein target (about 1.6 g/kg/day, within the usual 1.4-2.2 range) from varied sources (soy, legumes, seitan, grain-legume combinations, or plant protein powders), spread across meals, with leucine-rich servings (~700-3000 mg leucine per dose). The modest edge for animal protein should not override a client's preferences or ethics.
**Evidence:** Across 9 RCTs (n=266), soy protein gave the same strength and lean-mass gains as whey or other animal proteins. In 16 RCTs, source did not change absolute lean mass or strength overall, but animal protein favoured percent lean mass and adults under 50 gained slightly more lean mass with it (+0.41 kg, 95% CI 0.08-0.74). In a 12-week training study with protein matched at ~1.6 g/kg/day, habitual vegans and omnivores both gained 1.2 kg leg lean mass with no between-group differences.
**Grade:** moderate
**Applies to:** Healthy adults with total protein generally above the RDA. The training study was in 38 untrained young men with self-selected diets. Messina's comparisons were supplement trials.
**Individual variation / conflicts:** The meta-analyses partly disagree about younger adults, with a possible small advantage for animal protein. Evidence on whole-food vegan diets and in older adults is limited.
**Sources:** [S202], [S203], [S241], [S185]

### Protein powder is a convenience, not a requirement
**Rule:** Set the daily protein target first, spread over 3-4 meals of about 20-40 g. Suggest whey or another protein powder only when food alone makes the target hard (appetite, budget, time, vegetarian diet). Otherwise legumes, dairy, eggs, fish and meat are fine. ISSN's 2.3-3.1 g/kg figures refer to trained people in a deficit and are not general advice.
**Evidence:** The ISSN states that whole foods can meet needs and supplements are a practical way to reach quality and quantity targets. Protein supplementation during ≥6 weeks of resistance training added +0.30 kg FFM and +2.49 kg 1RM, plateauing around 1.62 g/kg/day total intake.
**Grade:** moderate
**Applies to:** Healthy adults doing resistance training. Benefit declines with age. Clients with kidney disease need medical guidance.
**Individual variation / conflicts:** The average effect is small. Morton's senior author declares dairy-council funding and ISSN authors have industry ties.
**Sources:** [S185], [S186]

### Very high protein intakes and supplement dose
**Rule:** Do not prescribe more than 3 g/kg/day as a fat-loss strategy. If a supplement is used, about one serving (~25-35 g) a day alongside resistance training is usually enough. Prioritise whole-food protein.
**Evidence:** The ISSN calls the evidence that >3.0 g/kg/day improves body composition in trained people "novel", meaning preliminary. A 2026 network meta-analysis (36 RCTs, n=1,552, ≥6 weeks of supervised training) found whey gave the largest lean-mass gain versus placebo (+1.24 kg, 95% CrI 0.61-1.87), with its dose-response plateauing at about 30-35 g/day.
**Grade:** emerging
**Applies to:** Healthy adults who exercise. The older-adult subgroup (9 trials) is small and its rankings may be unstable.
**Individual variation / conflicts:** The authors call the dose estimate exploratory and rate plant-protein comparisons low to very low certainty. In adults 65+, whey's advantage narrowed and casein ranked higher. ISSN authors include supplement-industry affiliations; the network meta-analysis authors declare none.
**Sources:** [S185], [S207]

## Carbohydrate, fat, fibre and sugars

### Macronutrient ranges for health
**Rule:** Once protein is set, place carbohydrate and fat within roughly 45-60% and 20-35% of energy, adjusted for preference and training volume. Keep saturated fat below 10% of energy and trans fat minimal. Going outside these ranges (for example, low-carb) is acceptable when justified by adherence and preference, not as a superior fat-loss method.
**Evidence:** EFSA's reference ranges for adults are 45-60% of energy from carbohydrate and 20-35% from fat, adopted by AESAN. WHO (2023) advises total fat ≤30%, saturated fat ≤10% and trans fat ≤1%. EFSA says saturated and trans fatty acids raise LDL cholesterol in a dose-dependent way and that saturated fat intake should be as low as possible within an adequate diet.
**Grade:** strong
**Applies to:** Healthy adults; population health ranges, not athletic fuelling targets.
**Individual variation / conflicts:** WHO caps total fat at 30% while EFSA goes to 35%. High-protein diets may push carbohydrate or fat toward the bottom of the ranges, which is fine if fibre and fat quality stay adequate.
**Sources:** [S795], [S205], [S184]

### Carbohydrate by training load
**Rule:** Set carbohydrate in g/kg from actual training load, not as a fixed percentage. A typical gym client training about 3-5 h per week sits in the light tier (about 3-5 g/kg/day) and can go lower in a deficit if they prefer. Use 5-7 g/kg only for about 1 h/day or more of moderate-to-hard training (usually conditioning or endurance work added to lifting), and more than 6 g/kg only for genuine multi-hour endurance volume. Recheck when training volume changes.
**Evidence:** The 2016 ACSM/AND/DC position sets light activity at 3-5 g/kg/day, moderate (~1 h/day) at 5-7, high (1-3 h/day endurance) at 6-10, and very high (>4-5 h/day) at 8-12. The ISSN agrees that general-fitness people can meet needs with a normal diet (45-55% of energy, about 3-5 g/kg/day).
**Grade:** strong
**Applies to:** Healthy adults 18-65. Higher tiers come from endurance and team-sport athletes fuelling performance. No separate g/kg guidance for older adults was found.
**Individual variation / conflicts:** The ISSN is internally inconsistent: it also says "athletes and active individuals" should eat 5-8 g/kg/day; resolve this by actual training hours. Needs vary with body size, energy budget, goal and preference.
**Sources:** [S325], [S326]

### Lifters do not need high-carbohydrate diets
**Rule:** Do not raise carbohydrate above about 3-5 g/kg/day just because a client lifts. Choose the carbohydrate-to-fat split within the energy target by preference, adherence and fullness, once protein and the fat floor are met. Consider more carbohydrate only for very high-volume sessions (more than 10 hard sets per muscle group), two sessions a day, or added endurance work.
**Evidence:** A 2022 systematic review of 49 studies found higher carbohydrate did not improve fed-state resistance-training performance for up to about 10 sets per muscle group, and 15 of 17 long-term studies found no effect on strength gains. Benefits appeared mainly versus fasted controls, above 10 sets per muscle group, or after glycogen-depleting twice-daily sessions.
**Grade:** moderate
**Applies to:** Resistance-trained and recreationally active adults, mostly young men (39 of 49 studies in strength trainees or athletes).
**Individual variation / conflicts:** Conflicts with ISSN's 5-8 g/kg/day figure, which comes from endurance research. Few trials were isocaloric or used matched placebos.
**Sources:** [S327]

### Carbohydrate around long or fasted sessions
**Rule:** If a client trains fasted early in the morning or does long sessions (more than about 45 min with many hard sets), suggest a carbohydrate-containing snack or meal beforehand, or a drink during the session. A large dose is not needed. For short fed-state sessions, carbohydrate timing matters little.
**Evidence:** A meta-analysis of 21 crossover studies (n=226) found carbohydrate before or during resistance exercise increased session volume (SMD 0.61, 95% CI 0.11-1.11; I² 79%; GRADE low), concentrated in sessions over 45 min (SMD 1.02) and after fasts of 8 h or more (SMD 0.39). Dose and load did not moderate the effect.
**Grade:** moderate
**Applies to:** Young, almost all male, mostly trained adults in acute lab sessions. The outcome is volume in one session, not long-term gains.
**Individual variation / conflicts:** Low certainty and high heterogeneity. Whether more volume per session leads to more long-term hypertrophy in recreational lifters is not shown.
**Sources:** [S328]

### Minimum dietary fat
**Rule:** Keep fat at or above about 20% of energy and not below about 0.5 g/kg/day for any long period, including during a cut; default range 20-35%. If a client wants less fat during a hard deficit, keep it short and make sure essential fatty acids are covered.
**Evidence:** The 2016 ACSM/AND/DC position says athletes should be discouraged from chronic fat intakes below 20% of energy, which lower intake of fat-soluble vitamins and essential fatty acids, with no performance benefit. EFSA's range is also 20-35%. The ISSN suggests 0.5-1.5 g/kg/day for general fitness and 0.5-1 g/kg/day during fat loss.
**Grade:** strong
**Applies to:** Healthy adults of both sexes, including recreational gym-goers.
**Individual variation / conflicts:** ISSN's 0.5-1 g/kg can fall below 20% of energy at high intakes; use whichever floor is higher. The 20% floor rests on micronutrient and fatty-acid adequacy and expert judgement, not dose-response trials.
**Sources:** [S325], [S330], [S326]

### Essential fatty acids
**Rule:** Check the diet regularly includes alpha-linolenic acid sources (walnuts, flax, chia, rapeseed oil) and oily fish (for example 1-2 servings a week) to approach 250 mg/day EPA+DHA. Vegetarians and vegans can consider an algal EPA/DHA supplement. Prefer unsaturated fats (extra-virgin olive oil, nuts, fish) over butter and fatty processed meats, especially when total fat is low.
**Evidence:** EFSA adequate intakes for adults: linoleic acid 4% of energy, ALA 0.5% of energy, EPA+DHA 250 mg/day (plus 100-200 mg/day DHA in pregnancy and lactation); saturated and trans fats as low as possible.
**Grade:** strong
**Applies to:** Healthy European adults, including pregnancy and lactation; population reference values.
**Individual variation / conflicts:** FAO/WHO sets lower linoleic acid values (2-3% of energy); EFSA's reflects European intakes. An adequate intake is assumed adequate, not a proven requirement. The fish-servings figure is practical guidance, not from the sources.
**Sources:** [S330], [S331]

### Dietary fibre
**Rule:** Set a floor of at least 25 g/day of fibre (ideally 25-35 g) from whole grains, legumes, vegetables and fruit, including during fat loss and high-protein phases, plus at least 400 g/day of vegetables and fruit. Increase gradually, with fluids, to limit GI discomfort.
**Evidence:** EFSA considers 25 g/day adequate for bowel function; WHO (2023) recommends ≥25 g/day naturally occurring fibre and ≥400 g/day of vegetables and fruit. Reynolds 2019 (185 prospective studies, 58 trials) found 15-30% lower all-cause and cardiovascular mortality and less coronary heart disease, stroke, type 2 diabetes and colorectal cancer at the highest intakes, with the greatest reduction at 25-29 g/day and possible further benefit above.
**Grade:** strong
**Applies to:** Adults without chronic disease. Hard outcomes are observational; weight, blood pressure and cholesterol effects come from RCTs.
**Individual variation / conflicts:** People with IBS or IBD may need individual adjustment of fibre type and amount.
**Sources:** [S206], [S205], [S795]

### Free sugars: limits
**Rule:** Present free sugars as something to minimise, not a quota to fill. Use below 10% of energy as the firm upper limit and below 5% (about 25 g/day) as the ideal, calculated from the client's own target (for example, 50 g at 2000 kcal). Count juice, honey, syrups, soft drinks and sweets; do not count whole fruit or plain milk and yoghurt. Priority actions: water instead of sugar-sweetened drinks, whole fruit instead of juice, unsweetened dairy.
**Evidence:** WHO (2015) strongly recommends free sugars below 10% of energy and conditionally below 5%. EFSA (2022) could not set a safe level and concluded added and free sugars should be "as low as possible in the context of a nutritionally adequate diet"; RCTs support causal links with obesity and dyslipidaemia at moderate certainty. AESAN (2022) endorses this, says juice should not replace whole fruit, and links sugar-sweetened beverages to weight gain, type 2 diabetes, cardiovascular disease and premature death.
**Grade:** strong
**Applies to:** General adult population in the EU and Spain. Sports drinks or gels during long endurance sessions are a separate, deliberate use.
**Individual variation / conflicts:** The 5% target is conditional (weaker evidence). There is no numeric EU limit, so WHO's figures are the only quantitative anchor. Prospective cohorts showed no relationship when sugars were exchanged isocalorically, so how much harm is purely from extra energy is unsettled. Very active people have a larger absolute allowance.
**Sources:** [S338], [S339], [S340]

### Sugar and body weight work through energy intake
**Rule:** Explain that sugar is not uniquely fattening at equal calories; it makes over-eating easy, especially in liquid form. Cutting sugary drinks and sweets is one of the most effective low-friction ways to reduce calories. Within a set energy and macronutrient target, a small amount of sugar does not hurt fat loss.
**Evidence:** In ad libitum trials, reducing sugars lowered weight by 0.80 kg and increasing them raised it by 0.75 kg; swapping sugars for other carbohydrates at equal calories did not change weight (0.04 kg). In cohorts, the highest sugar-sweetened beverage intake was linked to higher odds of overweight or obesity (OR 1.55).
**Grade:** moderate
**Applies to:** General adults (and children in cohort data), short-to-medium-term trials.
**Individual variation / conflicts:** Trials varied. "Sugar is toxic regardless of calories" goes beyond this evidence.
**Sources:** [S341]

## Diet patterns

### Low-carb and low-fat give similar weight loss
**Rule:** Do not sell low-carb or low-fat as metabolically superior for fat loss. Let the client choose the split they can sustain, set a moderate deficit, keep protein adequate and favour minimally processed foods in either version.
**Evidence:** In a network meta-analysis of 121 RCTs (n=21,942), 6-month loss versus usual diet was 4.63 kg (low-carb) and 4.37 kg (low-fat), largely gone by 12 months. In 48 RCTs (n=7,286), 12-month losses were 7.25 and 7.27 kg. In DIETFITS (n=609, 12 months), healthy low-carb lost 6.0 kg and healthy low-fat 5.3 kg (difference 0.7 kg, 95% CI -0.2 to 1.6). Obesity Canada states calorie-restricted patterns with varying macronutrients give similar loss over 6-12 months.
**Grade:** strong
**Applies to:** Adults with overweight or obesity in 6-24-month trials. Less data in normal-weight recreational lifters, though the energy-balance logic holds.
**Individual variation / conflicts:** Tobias 2015 (53 RCTs) found low-carb beat low-fat by 1.15 kg, statistically significant but clinically trivial. Individual responses vary widely within each arm.
**Sources:** [S208], [S209], [S210], [S211], [S212]

### No metabolic advantage for low-carb at equal calories
**Rule:** Tell clients that at equal calories and protein, the carbohydrate-to-fat ratio does not meaningfully change fat loss. Any benefit of low-carb comes from eating fewer calories (appetite, food choice), not "insulin magic". Choose it only if it helps that person eat less sustainably, and do not demonise carbohydrate or fat.
**Evidence:** A meta-analysis of 32 controlled feeding studies (563 subjects; carbohydrate 1-83% of energy) found slightly greater energy expenditure (+26 kcal/d) and fat loss (+16 g/d) on lower-fat diets, the opposite of the carbohydrate-insulin prediction, and called the effects physiologically meaningless. In a 4-week inpatient crossover (n=20), people ate 689 kcal/d less on an ad libitum plant-based low-fat diet than on an animal-based ketogenic diet.
**Grade:** moderate
**Applies to:** Adults, mostly with overweight or obesity, in short, tightly controlled metabolic-ward studies.
**Individual variation / conflicts:** Some people feel low-carb controls appetite better, and the ad libitum ward result may not hold outside. The meta-analysis was done by one group inside a narrative review.
**Sources:** [S216], [S217]

### Adherence predicts results better than diet type
**Rule:** Make sustainability the main criterion when choosing a diet. Ask about food preferences, schedule, culture and budget. Track adherence (logging, regular check-ins) as the main process metric, and change the approach when adherence falls rather than adding restriction.
**Evidence:** In a 1-year RCT of Atkins, Zone, Weight Watchers and Ornish (n=160), weight loss correlated with adherence (r=0.60) but not diet type (r=0.07), and only 50-65% per arm finished. In POUNDS Lost (n=811, 2 years), each group session attended was associated with 0.2 kg more loss, and satiety and satisfaction were similar across arms. A 48-trial network meta-analysis supported "recommending any diet that a patient will adhere to".
**Grade:** moderate
**Applies to:** Adults with overweight or obesity in weight-loss trials (Dansinger: age 22-72, BMI 27-42, with cardiometabolic risk factors).
**Individual variation / conflicts:** Adherence was self-reported and associations are correlational. The most adherable pattern differs by person and cannot be predicted in advance.
**Sources:** [S213], [S214], [S209]

### No single best eating pattern
**Rule:** Present several evidence-based patterns as valid options and let the client choose within a shared core: mostly minimally processed foods, plenty of plants, healthy fats and adequate protein. Do not present Mediterranean eating as a weight-loss tool on its own, because it still needs an energy deficit. Refer people with obesity-related disease or complex medical needs to a registered dietitian.
**Evidence:** Obesity Canada states there is "no one-size-fits-all eating pattern", recommends plans personalised to values and preferences (Level 4, Grade D), and recommends dietitian-led medical nutrition therapy for adults with obesity (Level 1a, Grade A). Acceptable patterns include partial meal replacements, DASH, portfolio, vegetarian, Nordic, low-GI, intermittent or continuous calorie restriction, and Mediterranean (graded mainly for glycaemia and triglycerides, little effect on weight). The AHA 2021 statement emphasises energy balance, fruit and vegetables, whole grains, mostly plant protein plus fish, liquid plant oils, minimally processed foods, little added sugar and salt, and limited alcohol.
**Grade:** moderate
**Applies to:** Adults in general, including adults with obesity and cardiovascular prevention.
**Individual variation / conflicts:** Graded moderate because the personalisation recommendation itself is expert opinion (Grade D); the stronger claim that weight loss is similar across patterns when calories match is covered, graded strong, in "Low-carb and low-fat give similar weight loss". Each pattern's evidence differs by outcome.
**Sources:** [S212], [S215]

### Genotype or insulin-based diet matching
**Rule:** Do not recommend DNA- or insulin-test-based "diet type" products for choosing between low-carb and low-fat. Choose by preference and adherence.
**Evidence:** In DIETFITS (n=609), there was no diet × genotype interaction (3-SNP pattern, P=.20) and no diet × insulin-30 interaction (P=.47) for 12-month weight loss.
**Grade:** emerging
**Applies to:** Adults 18-50 without diabetes, BMI 28-40. Only one genotype panel was tested.
**Individual variation / conflicts:** A clear null result, but from a single trial and panel.
**Sources:** [S210]

### Ketogenic diets: faster early loss, higher LDL
**Rule:** If a client wants keto, treat it as an option, not a requirement. Suggest a lipid panel (LDL, ideally apoB) at baseline and after 2-3 months, especially for lean clients or those with high LDL or a family history of heart disease. Emphasise unsaturated fats, keep protein and resistance training high to protect lean mass, and plan a sustainable long-term pattern.
**Evidence:** An umbrella review (17 meta-analyses, 68 RCTs, median 13 weeks) graded the LDL-C increase as high quality and the extra weight loss as moderate quality, and found reduced muscle mass with ketogenic LCHF in healthy participants. A 2025 meta-analysis (174 RCTs, n=11,481) found carbohydrate-restricted diets lowered triglycerides (-15.1 mg/dL) and systolic pressure (-2.1 mmHg) but raised LDL (+4.8 mg/dL), with keto giving more loss and larger LDL increases. In normal-weight adults (3 RCTs), LDL-C rose 1.08 mmol/L and apoB 0.35 g/L.
**Grade:** strong
**Applies to:** Adults, mostly with overweight or obesity, over short follow-ups. LDL and lean-mass concerns are larger in normal-weight adults (3 small RCTs).
**Individual variation / conflicts:** The strong grade applies to the LDL increase; the extra weight loss is moderate-quality and shrinks over time. Very-low-calorie ketogenic diets in obesity did not worsen LDL or muscle mass. LDL response varies a lot. No long-term trials of cardiovascular events exist.
**Sources:** [S218], [S219], [S220]

### Ketogenic diet combined with training
**Rule:** Do not recommend keto as a better fat-loss or recomposition approach for gym clients. If a client prefers it, it can work as a way to reduce calories, but keep protein high and watch strength and training quality. Point out that early weight loss partly reflects glycogen and water.
**Evidence:** A network meta-analysis of 78 RCTs (n=5,219, healthy adults 18-65) ranked calorie restriction plus exercise best for weight, body-fat % and lean-mass preservation; keto plus exercise ranked lowest for body-fat % (+3.14 points vs calorie restriction plus exercise, 95% CI 0.52 to 5.75) and lean mass.
**Grade:** emerging
**Applies to:** Healthy adults 18-65 in heterogeneous diet-plus-exercise trials.
**Individual variation / conflicts:** Indirect comparisons with wide intervals; most lean-mass CIs crossed zero. Adherence to keto varies widely.
**Sources:** [S329]

### Mediterranean diet and cardiovascular events
**Rule:** Recommend a Mediterranean-style pattern (extra-virgin olive oil as main fat, nuts, legumes, vegetables, fruit, whole grains, fish, little processed meat) as a strong default for heart health, especially for older or high-risk clients. Describe the benefit as a probable reduction in cardiovascular events, not a proven mortality benefit.
**Evidence:** PREDIMED (republished 2018; 7,447 adults aged 55-80 at high risk, 4.8 years) found HR 0.69 (olive oil) and 0.72 (nuts) for major cardiovascular events versus low-fat advice. CORDIOPREV (1,002 coronary patients, 7 years) found adjusted HRs 0.72-0.75, clear in men (HR 0.67) but not in 175 women. Cochrane 2019 rated the stroke reduction (HR 0.60) moderate quality and found little or no effect on CVD or total mortality (low quality).
**Grade:** moderate
**Applies to:** Older Spanish adults at high cardiovascular risk and mostly male coronary patients. Applying it to young healthy gym-goers rests mainly on observational data.
**Individual variation / conflicts:** PREDIMED had randomisation irregularities and was retracted and republished. CORDIOPREV discloses olive-oil foundation funding.
**Sources:** [S221], [S222], [S223]

### Mediterranean diet: risk factors and weight
**Rule:** Use the Mediterranean pattern for long-term health and adherence. When the goal is fat loss, still create an energy deficit within it, and do not promise faster weight loss from the pattern alone.
**Evidence:** An umbrella review (80 articles, 495 meta-analyses of RCTs) rated the Mediterranean diet as having the most consistent evidence, with suggestive improvements in weight, BMI, cholesterol, glucose and blood pressure. In a 121-trial network meta-analysis, only the Mediterranean diet kept its risk-factor benefits at 12 months. For weight, 5 RCTs (n=998, ≥12 months) found it beat low-fat diets but matched other comparators.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity or cardiometabolic risk.
**Individual variation / conflicts:** 81% of the underlying articles were low or critically low quality. Mancini found it generally similar to comparators for blood pressure and lipids during weight loss.
**Sources:** [S224], [S225], [S208]

### Intermittent fasting and time-restricted eating
**Rule:** Offer time-restricted eating or other fasting schedules only as a structure for clients who find it easier to control intake that way, and still set a total calorie target. Do not claim fat-loss benefits beyond the deficit. Avoid it for people with a history of disordered eating, and coordinate with the clinician for anyone on glucose-lowering medication.
**Evidence:** A 2025 BMJ network meta-analysis (99 RCTs, n=6,582) found all fasting and continuous-restriction strategies beat ad libitum eating; only alternate-day fasting beat continuous restriction (-1.29 kg), mainly in trials under 24 weeks. In a 12-month RCT (n=139) with calorie restriction in both arms, 8-hour TRE gave -8.0 kg versus -6.3 kg (difference not significant, P=0.11). In TREAT, 16:8 without calorie guidance did no better than three meals a day (-0.26 kg). An umbrella review found 72% of significant associations rested on very-low-quality evidence.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity, many with health conditions; most trials are short (median about 3 months).
**Individual variation / conflicts:** Fernandes-Alves 2026 (30 studies) reported 1.46 kg more loss with TRE even versus isocaloric controls; Sun 2025 found -0.94 kg but concluded no added benefit. Short trials and imperfect calorie matching probably explain the differences.
**Sources:** [S226], [S227], [S228], [S229], [S230]

### Time-restricted eating and lean mass
**Rule:** If a client uses TRE, combine it with progressive resistance training and adequate protein spread over at least 2-3 feedings in the eating window. Track strength and waist or body composition, not scale weight alone. Be more cautious with older adults.
**Evidence:** Some meta-analyses find small FFM losses (Sun 2025: -0.58 kg; Fernandes-Alves 2026: -0.41 kg versus isocaloric controls; TREAT: lower appendicular lean mass index, -0.16 kg/m²), and an umbrella review associated fasting with reduced FFM. Others find no significant loss (Moon 2020: -0.24 kg; He 2024: -0.56 kg, P=0.06; Hays 2025 with exercise; Ali 2026 in trained people: FFM +0.27 kg, fat -1.25 kg).
**Grade:** emerging
**Applies to:** Adults with overweight or obesity and small samples of young trained people; short trials; thin data in older adults.
**Individual variation / conflicts:** The meta-analyses conflict. Lean-mass loss probably depends on deficit size, protein and training rather than the eating window, and part of it may be water or glycogen.
**Sources:** [S229], [S231], [S230], [S228], [S232], [S233], [S234], [S235]

### Vegetarian and vegan diets lower LDL
**Rule:** Support clients who choose vegetarian or vegan eating. Describe the lipid benefit honestly as a modest LDL reduction, and focus on a well-planned whole-food version (legumes, soy, whole grains, nuts) rather than plant-based ultra-processed foods.
**Evidence:** A meta-analysis of 30 RCTs found reductions in total cholesterol (-0.34 mmol/L), LDL-C (-0.30 mmol/L) and apoB (-12.9 mg/dL) versus omnivorous diets, consistent across age, continent, health status and duration. The Academy of Nutrition and Dietetics considers well-planned vegetarian and vegan diets healthful, adequate and suitable for all life stages and athletes.
**Grade:** strong
**Applies to:** Adults, healthy or with cardiometabolic risk.
**Individual variation / conflicts:** The apoB estimate is imprecise. Part of the change may come from weight loss or less saturated fat. The AND position is a narrative synthesis relying on observational data for hard outcomes. LDL response varies.
**Sources:** [S236], [S237]

### Plant-based diets and hard outcomes
**Rule:** Describe the plant-based heart benefit as likely but observational and partly explained by lower weight, blood pressure and cholesterol. Do not claim it lowers overall mortality. Make sure vegetarian diets are nutritionally complete (B12, adequate protein and micronutrients).
**Evidence:** A meta-analysis of 10 cohorts linked vegetarian diets to lower ischaemic heart disease (RR 0.75) and total cancer incidence (RR 0.92), but not to all-cause, cardiovascular or cancer mortality. In EPIC-Oxford (48,188 people, 18 years), vegetarians had 22% lower ischaemic heart disease (HR 0.78; 0.90 after adjusting for BMI, blood pressure, cholesterol and diabetes) and 20% higher total stroke (HR 1.20), about 10 fewer heart disease cases and 3 more strokes per 1,000 people over 10 years.
**Grade:** emerging
**Applies to:** Western, often health-conscious, mostly middle-aged cohorts.
**Individual variation / conflicts:** Observational and open to confounding. The stroke signal comes from one cohort and its cause is unclear.
**Sources:** [S238], [S239]

### Vitamin B12 for vegans and vegetarians
**Rule:** For any vegan client, and vegetarians with low dairy and egg intake, a regular B12 supplement or reliably fortified foods is non-negotiable. Suggest a GP check (serum B12, ideally with holoTC or MMA) if they have not supplemented for a while. Leave dosing to the clinician or product label.
**Evidence:** The Academy of Nutrition and Dietetics states vegans need fortified foods or supplements. A 2024 meta-analysis (17 studies) found adult vegans had lower serum B12 and higher homocysteine than omnivores, with trends indicating functional deficiency; supplementing vegans had better values on all biomarkers.
**Grade:** strong
**Applies to:** Adult vegans and vegetarians. Older adults also absorb B12 less well (not quantified here).
**Individual variation / conflicts:** Serum B12 alone is an imperfect marker. Unsupplemented long-term vegans are at highest risk.
**Sources:** [S237], [S240]

### Ultra-processed foods and energy intake
**Rule:** Build the diet mainly around minimally processed foods, which tends to lower calorie intake on its own. Do not treat a NOVA label as decisive: plain yoghurt, wholegrain bread, canned legumes and protein powders can be useful. Focus on cutting energy-dense, hyper-palatable products (pastries, snacks, sugary drinks, fast food).
**Evidence:** In an inpatient crossover (n=20), an ultra-processed diet matched for presented calories and nutrients led to 508 ± 106 kcal/day more intake (+0.9 kg vs -0.9 kg). In UPDATE (50 analysed, 8 weeks, both diets following UK guidance), the minimally processed diet produced more weight loss (-2.06% vs -1.05%). A 2026 meta-analysis of 10 RCTs found more weight gain (SMD 0.65) and faster eating (SMD 0.96) on UPF diets; the energy-intake effect was SMD 0.71 when the UPF diet was more energy-dense and 0.02 when energy density was similar (low certainty).
**Grade:** moderate
**Applies to:** Adults, mostly with overweight or obesity, in short trials with provided food. Lean trained clients were not studied.
**Individual variation / conflicts:** Whether processing itself matters, or only nutrient profile and energy density, is disputed. AESAN attributes harm mainly to ingredients rather than processing techniques. Hall 2019 included only 20 people over 2 weeks.
**Sources:** [S342], [S343], [S344]

### Ultra-processed foods and health outcomes
**Rule:** Describe high UPF intake as consistently associated with worse cardiometabolic and mental-health outcomes and higher mortality, mostly in observational data with low certainty. Avoid fear-based or absolute claims. Practical message: minimally processed foods as the base, energy-dense UPFs as occasional foods.
**Evidence:** An umbrella review of 45 pooled analyses (n≈9.9 million) found direct associations with 32 of 45 outcomes, including cardiovascular mortality (RR 1.50), type 2 diabetes (RR 1.12, GRADE moderate), anxiety, common mental disorders, all-cause mortality (RR 1.21) and obesity (OR 1.55). Only 4 analyses were moderate quality; 22 were low and 19 very low.
**Grade:** moderate
**Applies to:** General adult populations in observational studies; no exercise-specific data.
**Individual variation / conflicts:** Residual confounding by diet quality and socioeconomic status. NOVA groups very different foods together. AESAN attributes harm to ingredients rather than processing.
**Sources:** [S345], [S340]

### AESAN food-based guidance for Spain
**Rule:** For clients in Spain, build meal plans on these weekly frequencies and translate them into concrete Spanish meals: lentejas or garbanzos 4 or more times a week; fish 3 or more times (sardinas, caballa, salmón); meat no more than 3 times a week, mostly pollo or conejo, with embutidos as occasional food; a vegetable and a fruit at every main meal; olive oil as cooking and dressing fat; wholegrain bread or rice adjusted to calorie goals. For fat-loss clients, cap cereals at 4 servings/day.
**Evidence:** AESAN (2022): at least 3 servings/day of vegetables and 2-3 of fruit; tubers in moderation; 3-6 servings/day of cereals (no more than 4 if restricting calories), prioritising whole grains; at least 4 servings/week of legumes, building up to daily; 3+ servings/week of unsalted nuts (up to 1/day); 3+ servings/week of fish, prioritising oily fish; up to 4 eggs/week; at most 3 servings/day of dairy; at most 3 servings/week of meat, prioritising poultry and rabbit and minimising processed meat; olive oil daily; water as the main drink. Example servings: fish 125-150 g, meat 100-125 g, egg 53-63 g, milk 200-250 ml, yoghurt 125 g, cured cheese 40-60 g, olive oil 10 ml.
**Grade:** strong
**Applies to:** General Spanish adults; public-health guidance that also integrates environmental sustainability. Athletes or clients with medical conditions may need adjustment, for example higher protein from legumes, dairy, eggs and fish.
**Individual variation / conflicts:** The meat limit is for total meat; red- and processed-meat numbers cited in the report come from other frameworks (Mediterranean pyramid, EAT-Lancet). Meat and dairy limits are partly environmental. High-protein goals may need deliberate planning to stay within the meat cap.
**Sources:** [S251]

## Behaviour and self-monitoring

### Self-monitoring
**Rule:** Encourage simple, sustainable self-monitoring: logging food in an app (even partially, or photo logs), regular weighing judged by weekly trend, and tracking training sessions. Expect engagement to drop, so shrink tracking to the minimum the client will keep rather than demanding perfect logs. Use the data for feedback, not judgement. Do not push tracking on clients with a history of disordered eating; refer them instead.
**Evidence:** A review of 22 studies found a consistent association between self-monitoring and weight loss (weak evidence). A review of 39 RCTs of digital self-monitoring found more self-monitoring linked to weight loss in 74% of occurrences, with higher engagement in digital than paper arms in 21 of 34 comparisons; few achieved monitoring on 75% or more of days. Smartphone-app RCTs showed loss peaking at 2.18 kg at 3 months and 1.63 kg at 12 months versus control, which the authors call minimal.
**Grade:** moderate
**Applies to:** Adults with overweight or obesity in behavioural programmes, mostly white women; by extension to recreational lifters.
**Individual variation / conflicts:** Mostly associational. App effects come from multicomponent apps. The optimal frequency is unknown. Tracking can increase anxiety or obsessive behaviour in some people (see "Calorie tracking and eating-disorder risk").
**Sources:** [S263], [S264], [S265]

### Meal planning
**Rule:** Offer meal planning as a practical, optional tool: plan the next few days' main meals, write a shopping list, batch-cook and freeze, and keep default "emergency" meals. As coaching judgement (not tested evidence), start with a simple weekly template rather than a rigid day-by-day plan and adjust to what the client sustains.
**Evidence:** In 40,554 French adults (cross-sectional), 57% planned meals at least occasionally. Planners had better guideline adherence (OR 1.13) and food variety (OR 1.25); in women, lower odds of overweight (OR 0.92) and obesity (OR 0.79); in men, only lower odds of obesity (OR 0.81). AESAN also suggests batch-cooking to save time and energy.
**Grade:** emerging
**Applies to:** French adult volunteers with self-reported weight.
**Individual variation / conflicts:** Observational only; no RCT shows planning itself causes weight loss. Planners may differ in other healthy behaviours.
**Sources:** [S266]

## Food logging and measurement accuracy

### Logs under-report intake
**Rule:** Treat any logged or recalled calorie intake as a lower-bound estimate. Assume a typical client's log under-counts real intake by roughly 10-30%, possibly more. Never tell a client "you can't be gaining on X kcal" based on the log alone.
**Evidence:** A review of 59 DLW studies (6,298 adults) found significant under-reporting in most studies, including 16 technology-based ones. A meta-analysis of 31 DLW studies (4,518 adults) pooled underestimation of about 315-633 kcal/d in women and 422-822 kcal/d in men, depending on method. Pooled US biomarker data show average under-reporting of 15% with one 24-h recall and 28% with an FFQ.
**Grade:** strong
**Applies to:** Free-living adults in DLW validation studies (US, Europe, Australia). Research instruments, not consumer apps.
**Individual variation / conflicts:** Direction is consistent but magnitude varies widely, and some people over-report. Group averages cannot be applied as a fixed correction to one person.
**Sources:** [S295], [S289], [S296]

### Self-reported intake is poor for individuals
**Rule:** Do not compute a client's maintenance or deficit from their log, and do not "correct" a log by an average under-reporting factor. Use logs to change behaviour and spot patterns; use the weight trend (plus waist and photos) to judge energy balance.
**Evidence:** In the WHI biomarker study (n=450), FFQs, 4-day records and 24-h recalls explained only 3.8%, 7.8% and 2.8% of biomarker energy variation (41.7-44.7% after calibration with BMI, age and ethnicity). An AI photo app underestimated intake by 25% in 20 women with obesity (limits of agreement -3707 to +2073 kcal/d, ICC 0.00). Energy-balance researchers called self-reported energy intake unacceptable for scientific measurement.
**Grade:** moderate
**Applies to:** Postmenopausal US women, Swiss women with obesity and an expert opinion; applying this to coaching is an inference.
**Individual variation / conflicts:** Dhurandhar et al. is an opinion piece that drew commentaries, and Prentice et al. found calibrated self-report usable for epidemiology. Self-monitoring still aids adherence. Some disciplined people log well, but this cannot be known without an objective check.
**Sources:** [S301], [S302], [S303]

### Under-reporting rises with BMI
**Rule:** The heavier the client, the less weight to give their food log as a measure of calories. For clients with obesity, rely on the weight trend from the start and use the log mainly to understand food choices, timing and patterns.
**Evidence:** In pooled US data, BMI 30 versus 25 added about -6.7% energy bias for a 24-h recall and -5.0% for FFQs, on top of a reference bias of about -15% and -29%. In OPEN, DLW energy needs were 378 kcal/d (women) and 485 kcal/d (men) higher in obese than non-obese people, but self-report largely failed to detect this.
**Grade:** moderate
**Applies to:** US adults, mostly middle-aged and older, using research instruments.
**Individual variation / conflicts:** Age and education also predict under-reporting, and some lean dieters under-report substantially.
**Sources:** [S296], [S297]

### "I eat almost nothing and don't lose weight"
**Rule:** When a client says this, do not conclude they have a slow metabolism. Assume intake is under-counted and activity over-counted, and test this kindly against a 2-4-week weight trend. Refer only if there are clinical red flags.
**Evidence:** In 10 obese "diet-resistant" patients reporting under 1200 kcal/d, TEE and RMR were within 5% of predicted and thermic effects were normal, but they under-reported intake by 47 ± 16% and over-reported activity by 51 ± 75%.
**Grade:** emerging
**Applies to:** A small selected clinical subgroup of treatment-seeking US adults; the 47% figure is not a population estimate.
**Individual variation / conflicts:** Single small study, though its direction matches the wider DLW literature.
**Sources:** [S298]

### Sex differences in under-reporting
**Rule:** Do not assume women's logs are less reliable than men's, or the reverse. Use the same scepticism and the same weight-trend check for everyone.
**Evidence:** In OPEN, men under-reported by 12-14% (24HR) and 31-36% (FFQ), women by 16-20% and 34-38%, and one review found misreporting more frequent in females for recalls. But the 2021 DLW meta-analysis found no sex difference except for estimated food records (men under-reported more), and pooled US data found no significant sex difference.
**Grade:** moderate
**Applies to:** Adults in DLW validation studies in high-income countries.
**Individual variation / conflicts:** Sources genuinely disagree. BMI, dieting and social desirability matter more than sex.
**Sources:** [S295], [S299], [S289], [S296]

### Weighing food does not remove under-reporting
**Rule:** Do not promise that weighing everything makes the log accurate. Weighing fixes portion size, but forgotten snacks, drinks, oils, sauces, tastes and weekend eating remain. Prompt for these specifically and still check the log against the weight trend.
**Evidence:** Weighed food records gave the largest pooled underestimation in men (about -820 kcal/d; 5 studies). In a 7-day weighed-record DLW study, 10 non-dietitian women under-reported by 429 ± 142 kcal/d, and 10 dietitians by 223 ± 116 kcal/d (not significant).
**Grade:** moderate
**Applies to:** Free-living adults; few studies and small samples.
**Individual variation / conflicts:** Controlled studies with pre-weighed foods show small app error, but they test database accuracy, not habitual reporting, so the findings are compatible.
**Sources:** [S295], [S300]

### Teach clients to log well
**Rule:** Teach clients to weigh calorie-dense foods, log oils and drinks, log at the time of eating, and include weekends. Judge intake from multi-day averages including weekends (7 days is a sensible minimum, a practical inference), never from one day.
**Evidence:** Dietitians under-reported less than non-dietitians on weighed records (223 vs 429 kcal/d). Averaging three 24-h recalls rather than one raised the correlation with true intake only from 0.26 to 0.31.
**Grade:** emerging
**Applies to:** Small samples of US women (n=10 per group) and pooled US validation studies.
**Individual variation / conflicts:** The expertise evidence is one small study, and even dietitians under-reported. Gains from extra days are modest.
**Sources:** [S300], [S296]

### Tracking apps versus reference methods
**Rule:** When food is fully and correctly entered, a mainstream app's calorie total is on average within roughly 5-10% of weighed intake, though single days can be further off. Most real-world error comes from what is missing or mismatched, not the app's arithmetic; a gap of about 200 kcal/d against reference methods is typical.
**Evidence:** A meta-analysis of 11 validation studies found apps underestimated energy by 202 kcal/d (I² 72%), shrinking to -57 kcal/d when the same food-composition table was used. With pre-weighed foods (n=44, 3 days), MyFitnessPal estimates were equivalent to weighed intake (mean error 3.7%); with a plated lab meal (n=43) it overestimated by 7.0%.
**Grade:** moderate
**Applies to:** Adults in high-income countries. The meta-analysis mostly used other self-report methods as reference; the MyFitnessPal trials measure estimation error, not omissions.
**Individual variation / conflicts:** Studies are heterogeneous, and controlled-feeding and free-living results measure different error sources.
**Sources:** [S304], [S305], [S306]

### Crowd-sourced app databases
**Rule:** Have clients prefer verified or lab-sourced entries, or barcode scans of the actual package, over user-submitted generic entries, and check that grams and kcal per 100 g are plausible. Treat sodium, cholesterol, saturated fat, fibre and micronutrient totals from consumer apps as unreliable.
**Evidence:** In Belgium (50 adults), MyFitnessPal energy correlated r=0.96 with the national database after removing 2.8% implausible entries; sodium and cholesterol were poor. In the US, five apps correlated 0.73-0.96 for energy and macronutrients, but each was low for some nutrients. Barcode scanning in 7 Dutch apps returned energy for 99% of products, 79% within 5%, with correct identification from 96% to 5%. Canadian endurance athletes' records showed poor MyFitnessPal validity but good Cronometer validity; Filipino adults self-logging in MyFitnessPal showed poor validity.
**Grade:** moderate
**Applies to:** Adults in Belgium, the US, Canada and the Philippines, and Dutch products; mostly researcher-entered data.
**Individual variation / conflicts:** Validation studies disagree; results depend heavily on which entries are chosen.
**Sources:** [S307], [S308], [S309], [S310], [S311]

### Apps are unreliable for saturated fat, cholesterol and sodium
**Rule:** Do not use consumer-app totals to manage saturated fat, cholesterol or sodium for a client with a cardiometabolic condition. Coach food choices instead, or use a verified database or a dietitian.
**Evidence:** Across 836 food codes, four consumer apps underestimated saturated fat by 13.8-40.3% and all five apps underestimated cholesterol by 26.3-60.3%; missing values were common (up to 62%), and within-app variation for saturated fat in meats and seafood was 74-145%. US and Belgian studies also found apps low or poorly correlated for cholesterol and sodium.
**Grade:** moderate
**Applies to:** Mainly database comparisons (Taiwanese and US foods).
**Individual variation / conflicts:** Magnitudes come from one Taiwan-centred study and will vary by country and cuisine; the direction is consistent.
**Sources:** [S312], [S307], [S308]

### AI photo and image-based logging
**Rule:** Photo or AI logging lowers the burden and can be suggested for adherence. Do not treat its calorie number as more reliable than manual logging; check it against the weight trend the same way.
**Evidence:** Against DLW, the SNAQ app underestimated by about 330 kcal/d in 30 normal-weight women and by 25% (-817 kcal/d, ICC 0.00) in 20 women with obesity, better than 24-h recall at group level but with no individual agreement. A mobile food record analysed by trained staff (45 adults) correlated with TEE at rho 0.58, with about 10-12% under-reporting, similar to traditional records.
**Grade:** emerging
**Applies to:** Swiss women and US adults aged 21-65; small samples; specific apps.
**Individual variation / conflicts:** Performance depends on the app, human analysis and cuisine. SNAQ AG was paid to develop the study version.
**Sources:** [S313], [S303], [S314]

### EU label rules and tolerances
**Rule:** Tell clients that a label's kcal figure is a calculated average and that EU control authorities tolerate deviations of about 20% for main macronutrients in the typical range. Do not argue over 10-20 kcal differences between label, app and scale. Weighing a labelled food with a correct entry is still the most precise thing a client can log.
**Evidence:** Under Regulation (EU) 1169/2011, declared values are averages from analysis or calculation, and energy is calculated with fixed factors (carbohydrate and protein 4 kcal/g, fat 9, alcohol 7, polyols 2.4, fibre 2, erythritol 0). The Commission's 2012 tolerance guidance allows, for carbohydrate, sugars, protein and fibre, ±2 g below 10 g/100 g, ±20% at 10-40 g and ±8 g above 40 g; for fat ±1.5 g, ±20% and ±8 g; for saturates ±0.8 g below 4 g/100 g and ±20% above. There is no separate energy tolerance.
**Grade:** strong
**Applies to:** Prepacked foods sold in the EU, including Spain. Not US rules or unlabelled restaurant food.
**Individual variation / conflicts:** The guidance is not legally binding, and enforcement varies by Member State.
**Sources:** [S315], [S316]

### Measured label and menu errors
**Rule:** Packaged-food labels are good enough for logging. Restaurant food is accurate on average, but single items can be off by 100+ kcal, and lower-calorie or "light" items tend to be understated (reduced-energy items averaged about 8-18% more than stated). Log sides, sauces and free extras separately; clients who eat out often should rely more on the weight trend.
**Evidence:** In 24 US snacks, measured energy was a median 4.3% above label. In 269 items from 42 US restaurants, stated energy was accurate overall (+10 kcal), but 19% had at least 100 kcal more than stated. Reduced-energy restaurant items averaged 18% and frozen meals 8% more than stated (not significant), with free sides raising energy to 245% of the entree's stated value. In 209 Portuguese prepacked foods, only half of higher-salt samples were within tolerance and 27% were out of tolerance for saturated fat.
**Grade:** emerging
**Applies to:** Mostly US foods; one EU compliance study (salt, fat, saturated fat only).
**Individual variation / conflicts:** Single small studies; reduced-energy differences were not significant; US figures may not transfer to Spain.
**Sources:** [S317], [S318], [S319], [S320]

### Atwater factors overstate whole almonds
**Rule:** Do not let clients cut whole almonds to "save calories" based on the logged number; the energy absorbed is probably about a quarter lower than logged. Spend scepticism instead on restaurant and "light" foods, where errors usually run the other way.
**Evidence:** In a controlled feeding study (n=18), measured metabolisable energy of almonds was 4.6 kcal/g (129 kcal per 28 g) versus 6.0-6.1 kcal/g predicted, a 32% overestimate.
**Grade:** emerging
**Applies to:** Healthy adults; whole almonds only.
**Individual variation / conflicts:** Single food and study; other nuts and processed forms were not tested.
**Sources:** [S321], [S319]

### Eyeballing portions versus weighing
**Rule:** For clients who want precision (a plateau or a cut), ask them to weigh calorie-dense foods (oils, nuts, cheese, rice, pasta, meats, spreads). A 1-2-week weighing period to recalibrate their eye is a practical heuristic, not a tested protocol. Otherwise use photo or atlas references and accept that eyeballed logs carry roughly ±20-80% error per item.
**Evidence:** In 128 adults estimating 59 foods and drinks from photos, unassisted error was 79.4% (44.8% with a food atlas, 67.8% for an AI model). In 120 US adults recalling a buffet, estimates were often more than 20% off regardless of aid or confidence. A review of 542 portion-size aids found image-based aids more accurate than food models or utensils.
**Grade:** emerging
**Applies to:** Adults in Kazakhstan and the US in lab or photo tasks.
**Individual variation / conflicts:** Error depends on food type and size; errors partly cancel across a day but cannot be relied on. Weighing does not fix omissions.
**Sources:** [S322], [S323], [S324]

## Supplements

### Creatine monohydrate for adults under 50
**Rule:** For a client doing regular resistance training who wants a supplement, creatine monohydrate 3-5 g/day, every day, at any convenient time, is the first and often only performance supplement to suggest. It needs no carbohydrate drink. Frame it as a modest add-on (about +1 kg lean mass over a training block) that never replaces training, protein and calories. Warn about a small early scale-weight increase that is not fat.
**Evidence:** A 2024 meta-analysis of 12 studies in adults under 50 found creatine plus resistance training increased lean mass by 1.14 kg (95% CI 0.69-1.59) and reduced body-fat % by 0.88% and fat mass by 0.73 kg versus training alone, regardless of training status, with no added benefit from carbohydrate; its authors estimate that 7 g or 0.3 g/kg of creatine per day is likely to add about 1 kg of lean mass versus training alone. Antonio 2021 gives the recommended dose as 3-5 g/day or 0.1 g/kg of body mass/day.
**Grade:** strong
**Applies to:** Healthy adults under 50, mostly young men, over weeks to months. Part of the lean-mass gain is intracellular water. For older adults see "Creatine in older adults".
**Individual variation / conflicts:** The sources' dose conversions do not match each other (0.1 g/kg is about 7 g at 70 kg, and 0.3 g/kg about 21 g), so this rule prescribes 3-5 g/day in grams and does not use per-kg conversions. ISSN authors have extensive creatine-industry ties; the independent meta-analysis agrees on direction (52% of its studies low risk of bias). Response varies between individuals.
**Sources:** [S242], [S243], [S244]

### Older adults: protein per meal
**Rule:** For clients over about 65, aim for a larger protein dose per meal than for young adults, roughly 0.4 g/kg per meal (about 28 g for a 70 kg person) at the main meals. Treat it as a practical target, not a threshold, and do not quote a leucine number.
**Evidence:** In a retrospective pooled analysis of acute studies in healthy men, myofibrillar protein synthesis plateaued after a single dose of 0.40 g/kg in older men (about 71 y) versus 0.24 g/kg in younger men (about 22 y), a borderline difference (p = .055); per kg of lean mass the gap was clearer (0.60 vs 0.25 g/kg, p < .01).
**Grade:** emerging
**Applies to:** Healthy men only, older compared with younger, single doses of high-quality protein at rest. Women, doses after resistance exercise and long-term outcomes were not studied.
**Individual variation / conflicts:** One retrospective analysis of acute muscle-protein-synthesis data with wide confidence intervals; long-term trials of protein distribution show no body-composition benefit when daily totals match (see "Protein distribution across meals"). The daily total (see "Older adults: protein targets") matters more.
**Sources:** [S802]

### Creatine in older adults
**Rule:** For clients about 60+ who already do resistance training 2-3 times a week, creatine 3-5 g/day is a reasonable optional add-on for muscle and leg strength. Present it as a small effect that only works with training, and have them clear it with their doctor if they have kidney disease, take multiple medications or have other conditions.
**Evidence:** A 2025 meta-analysis of 8 RCTs (n=482; 8-104 weeks) found improved lean tissue mass (SMD 0.27) and lower-limb strength (SMD 0.29, p=0.05) versus placebo plus training; upper-limb strength was not significant overall. In trials of 32 weeks or less, effects were larger (lean mass SMD 0.57; upper-limb SMD 0.45).
**Grade:** moderate
**Applies to:** Older adults combined with resistance training 2-3×/week; no benefit shown without training.
**Individual variation / conflicts:** Small effects, few trials, lower-limb CI touching zero, and an unexplained time-dependence.
**Sources:** [S245]

### Creatine safety and kidneys
**Rule:** Reassure healthy clients that standard creatine doses are not known to damage the kidneys. Tell them creatine raises blood creatinine, so they should mention it to their doctor before blood tests. Do not suggest creatine to anyone with known kidney disease, reduced eGFR, diabetes with kidney involvement or nephrotoxic medication without medical approval.
**Evidence:** The ISSN reports use up to 30 g/day for 5 years as safe in healthy people. A 2026 meta-analysis (20 trials) found serum creatinine rose by 0.13 mg/dL with no difference in urea or eGFR (MD -5.2 mL/min/1.73 m², 95% CI -15.0 to 4.6). A 2025 meta-analysis likewise found a small creatinine rise without a significant GFR change.
**Grade:** strong
**Applies to:** Healthy adults; most trials under 1 year; insufficient data in kidney disease.
**Individual variation / conflicts:** The 2025 paper calls the rise "transient" although its >12-week subgroup was significant, and its abstract appears to contain a unit error. The eGFR CI is wide and based on 8 trials. ISSN statements come from authors with industry ties.
**Sources:** [S242], [S246], [S247]

### Creatine questions: water, hair, cramps and loading
**Rule:** Answer the common creatine worries plainly: a loading phase is optional (3-5 g/day reaches the same muscle saturation in about 4 weeks); loading adds about 1-3 kg of scale weight, mostly water, early on; there is no good evidence that creatine causes hair loss, dehydration or cramps at recommended doses. Do not tell women they will respond exactly as men do.
**Evidence:** A 2021 narrative review by ISSN-affiliated authors concludes that the water gain from early loading (20 g/day) is short term and creatine "may not lead to water retention" over longer periods; no study has reported hair loss or baldness in humans and the evidence does not show raised testosterone or DHT; experimental and clinical research does not support claims of dehydration or cramping; 3-5 g/day for at least 4 weeks gives similar saturation to loading, and loading for 5-7 days typically adds 1-3 kg of body mass, mostly water.
**Grade:** moderate
**Applies to:** Healthy adults at 3-5 g/day; much of the underlying evidence comes from young male athletes.
**Individual variation / conflicts:** A narrative review, not a position stand; the lead author is CEO of the ISSN, which receives creatine-industry sponsorship, and the paper declares these ties. The hair-loss worry traces to one unreplicated study. The same review notes women may have higher resting muscle creatine, which may explain smaller responses in some studies.
**Sources:** [S244]

### Caffeine before training
**Rule:** Caffeine is optional. If a client wants it, the default for ordinary adults is up to about 3 mg/kg, 30-60 min before training, with no single dose above about 200 mg (EFSA); for 70 kg that means about 150-200 mg, roughly 1-2 espressos. The 3-6 mg/kg range is the ergogenic evidence base in trained people; mention it, but do not prescribe it as a default. Keep total intake at or below 400 mg/day, and 200 mg/day in pregnancy (see "Caffeine safety limits"). Avoid it late in the day if it disturbs sleep. Do not suggest it to people who are anxious, have palpitations, hypertension or heart problems, or are pregnant, without medical advice.
**Evidence:** The ISSN finds 3-6 mg/kg about 60 min before exercise consistently improves performance, with a minimum effective dose possibly as low as 2 mg/kg and frequent side effects at 9 mg/kg without extra benefit. An umbrella review of 21 meta-analyses found benefits for endurance, strength, muscular endurance, power and speed, mostly moderate quality and larger for aerobic exercise. EFSA (2015) considers single doses up to 200 mg safe for healthy adults, including less than 2 h before intense exercise, and habitual intake up to 400 mg/day.
**Grade:** strong
**Applies to:** Adults in general; most trials in young men, little data in women and older adults.
**Individual variation / conflicts:** The ISSN performance range (3-6 mg/kg, 210-420 mg at 70 kg) exceeds EFSA's 200 mg single-dose level at its upper end, so the default follows EFSA. Large individual differences (genetics, habitual intake, anxiety, sleep sensitivity). Several ISSN authors have supplement-industry ties.
**Sources:** [S248], [S249], [S250]

### Caffeine safety limits
**Rule:** Count total daily caffeine from coffee, tea, colas, energy drinks and pre-workouts, keeping it at or below 400 mg/day and single pre-training doses at or below about 200 mg. For pregnant or breastfeeding clients the limit is 200 mg/day. Avoid caffeine in the hours before bed. Discourage energy drinks, never mix them with alcohol, and check caffeine per scoop on pre-workout labels.
**Evidence:** EFSA (2015): habitual intake up to 400 mg/day (~5.7 mg/kg) raises no safety concern for healthy non-pregnant adults; single doses up to 200 mg are safe, including less than 2 h before intense exercise; 100 mg near bedtime may affect sleep; up to 200 mg/day in pregnancy and lactation. AESAN (2022) recommends reducing energy-drink consumption and avoiding them with hypertension, cardiovascular problems or sleep disorders, and flags the combination with alcohol.
**Grade:** strong
**Applies to:** Healthy adults. EFSA's exercise conclusion does not cover pregnant women, middle-aged or older adults doing intense exercise, or people with disease or medication.
**Individual variation / conflicts:** The ISSN performance dose (210-420 mg for 70 kg) can exceed EFSA's 200 mg single-dose level; it describes the evidence base in trained people, not the coach's default (see "Caffeine before training").
**Sources:** [S250], [S251]

### Vitamin D
**Rule:** Do not recommend vitamin D megadoses or routine blood testing to healthy adults to boost health, muscle or fat loss, and do not suggest vitamin D supplements to improve strength, muscle mass or physical performance. Encourage food sources and normal sun exposure, and refer for testing or treatment when there are risk factors or symptoms. For clients 75 and older, suggest discussing daily vitamin D with their doctor. Never tell a client to stop vitamin D their doctor prescribed.
**Evidence:** The Endocrine Society (2024, GRADE) suggests against empiric supplementation above the reference intake for healthy adults under 75 and against routine 25(OH)D testing, but suggests it for adults 75+, pregnancy and high-risk prediabetes. In VITAL (n=25,871, 2000 IU/day for 5.3 years), vitamin D did not reduce invasive cancer (HR 0.96) or major cardiovascular events (HR 0.97). For muscle, a meta-analysis of 54 placebo-controlled RCTs (8747 people, athletes excluded) found no benefit on strength, mass or performance, with a slightly slower timed up and go (MD 0.15 s) and lower knee flexion strength (MD -3.3 N); in 10 RCTs of community-dwelling adults over 50, vitamin D alone had no effect on handgrip strength (MD -0.07 kg) or appendicular lean mass and lowered SPPB scores (MD -0.23).
**Grade:** strong
**Applies to:** Adults without an established indication (osteoporosis treatment, malabsorption, documented deficiency).
**Individual variation / conflicts:** Optimal doses and targets remain unclear. Housebound, very covered or northern-latitude people may have indications a clinician should assess. An older meta-analysis found a small strength effect in people aged 65 and over; in the 54-trial analysis, studies of people with low vitamin D showed no benefit either. Diagnosing and treating a deficiency is for a clinician. Trained athletes are not covered by the muscle analyses.
**Sources:** [S252], [S253], [S824], [S825]

### Omega-3: fish rather than capsules
**Rule:** Do not recommend fish-oil capsules routinely for health, fat loss or muscle. Encourage regular fish, including oily fish, following national guidelines. Clients with high triglycerides or heart disease should decide on omega-3 products with their doctor, especially above 1 g/day.
**Evidence:** Cochrane (86 RCTs, 162,796 participants, mostly capsules) found little or no effect on all-cause mortality (RR 0.97) or cardiovascular events (RR 0.96) (high certainty), a possible slight reduction in coronary events (RR 0.91, low certainty), triglycerides about 15% lower, and no effect on adiposity. In 7 outcome RCTs (n=81,210), marine omega-3 supplements increased atrial fibrillation risk (HR 1.25), more above 1 g/day (HR 1.49).
**Grade:** moderate
**Applies to:** Adults at varying cardiovascular risk, mostly older (mean age 65 in the atrial fibrillation analysis), so application to young gym-goers is indirect.
**Individual variation / conflicts:** Evidence on fish intake itself is scarce. Prescription high-dose EPA products are a medical matter.
**Sources:** [S254], [S255]

### Supplement evidence tiers (ISSN 2018)
**Rule:** Use the ISSN 2018 tiers to sort supplements and generally suggest only category I. Category I (strong evidence, apparently safe): creatine monohydrate, protein and essential amino acids for muscle; beta-alanine, caffeine, carbohydrate, creatine, sodium bicarbonate, sodium phosphate, water and sports drinks for performance. Category II (limited or mixed evidence): for example BCAA, citrulline and nitrates. Category III (little to no evidence; do not suggest): for example glutamine, arginine, Tribulus terrestris, D-aspartic acid, CLA and chromium. Exception: do not suggest HMB for gaining muscle mass, although the ISSN lists it in category I for building muscle. Diet and training come first; supplements are optional extras.
**Evidence:** The ISSN review sorts supplements into I (strong evidence, apparently safe), II (limited or mixed) and III (little to no evidence) and advises generally recommending only category I. Independent meta-analyses disagree with its HMB listing: 11 studies with 302 participants aged 18-45 found no effect on fat-free mass, fat mass or strength; 6 RCTs in 193 trained and competitive athletes found trivial non-significant effects (fat-free mass ES 0.16); 10 trials with 596 older adults doing resistance training found no effect on appendicular lean mass, but modest gains in handgrip strength (SMD 0.24, borderline) and SPPB scores (SMD 0.54), with half the trials at high risk of bias.
**Grade:** moderate
**Applies to:** Athletes and recreationally active adults (ISSN society review); many underlying trials are in young trained men. The HMB meta-analyses cover adults aged 18-45, trained athletes and older adults doing resistance training.
**Individual variation / conflicts:** The ISSN review is a society position rather than a systematic review, and most authors declare supplement-industry ties. In older adults doing resistance training, HMB may modestly help physical function even without more lean mass; the exception is about muscle mass only. The IOC 2018 consensus names nitrate among the few supplements with good evidence, while the ISSN puts nitrates in category II. The detailed rules on creatine, caffeine and fat burners stay the reference; this rule is the overview.
**Sources:** [S326], [S821], [S822], [S823], [S256]

### Fat burners, weight-loss pills and BCAAs
**Rule:** Tell clients plainly that "fat burner" and weight-loss pills, and BCAA products, are a poor use of money for fat loss or muscle gain; spend the budget on food (protein, fruit, vegetables). Warn that supplements can be contaminated or mislabelled (stimulants, banned substances), and ask about any product a client already takes, especially with heart, blood-pressure or psychiatric medication.
**Evidence:** The IOC consensus states only a few performance supplements (including caffeine, creatine, specific buffering agents and nitrate) have good evidence, and some can harm health or contain prohibited substances. Of 315 RCTs on 14 weight-loss supplements and therapies, only 52 were low risk of bias with sufficient data, and only 16 of those showed significant differences (0.3-4.93 kg). A 2025 review of 22 BCAA RCTs found inconsistent evidence for strength, endurance or body composition, with possible reduced soreness.
**Grade:** moderate
**Applies to:** Adults. The IOC targets high-performance athletes; the BCAA review covers adults 18-72 at doses of 1.5-82 g/day.
**Individual variation / conflicts:** A few weight-loss products show small effects, but evidence quality is poor. The BCAA review could not pool data and did not compare BCAAs with matched whole protein.
**Sources:** [S256], [S257], [S258]

## Hydration and sodium

### Daily total water intake
**Rule:** Use 2.0 L/day (women) and 2.5 L/day (men) of total water, from drinks and food, as a reference, not a target to drink on top of food. Make water the default drink, drink more on training days and in hot weather, and use urine colour and thirst as everyday checks rather than counting litres.
**Evidence:** EFSA (2010) set adequate intakes of 2.0 L/day for women and 2.5 L/day for men; AESAN (2022) adopts them for everyone 18+, notes needs rise with activity, heat, fever and fluid losses, and recommends water as the main drink. EFSA's values assume that food supplies roughly 20-30% of total water and drinks 70-80%, as restated by two peer-reviewed survey papers (US data: 19% from food), so the totals correspond to roughly 1.6 L (women) and 2.0 L (men) from drinks.
**Grade:** strong
**Applies to:** Healthy adults at moderate temperature and activity. Not for medical fluid restriction (heart or kidney failure).
**Individual variation / conflicts:** These are adequate intakes from population data, not proven requirements. No evidence shows drinking well above them helps fat loss or health.
**Sources:** [S375], [S376], [S805], [S806]

### Older adults and thirst
**Rule:** Do not rely on thirst alone for clients about 65 and over. Offer at least 1.6 L (women) or 2.0 L (men) of drinks a day as a floor, not a target to force. Plan drinks at fixed times (with each meal, before and after training), keep a bottle visible during sessions, and refer to a GP if a client has dizziness, confusion or takes diuretics.
**Evidence:** The ESPEN geriatrics guideline (2019, recommendation 61, grade B) says older women should be offered at least 1.6 L and older men at least 2.0 L of drinks a day unless a clinical condition requires otherwise, derived from EFSA's total water intakes assuming 80% comes from drinks. AESAN (2022) flags dehydration as a particular problem in older adults because thirst perception is impaired and early fullness develops, most of all with cognitive or functional impairment, multiple chronic conditions or social vulnerability.
**Grade:** strong
**Applies to:** Older adults, especially frail ones; the effect in healthy, active older gym-goers is not quantified.
**Individual variation / conflicts:** Two guideline statements, without a quantitative meta-analysis. Medical fluid restriction (heart or kidney failure, some medicines) takes priority.
**Sources:** [S376], [S804]

### Fluid during exercise and sweat rate
**Rule:** For a typical 45-75 min gym session, arrive hydrated through normal drinking during the day (if clearly under-hydrated, drink about 5-7 mL/kg about 4 h before, and a further 3-5 mL/kg about 2 h before if urine is still dark or absent), then drink to thirst. For long or hot sessions, weigh before and after (minimal clothing, towel-dried): a loss under 2% is fine, over 2% means drinking more next time, and any weight gain means they drank too much.
**Evidence:** ACSM (2007) aims to prevent losses above 2% of body weight, notes wide individual variation in sweat rate and sodium, and recommends estimating sweat rate by weighing; a peer-reviewed review quotes its pre-exercise advice of 5-7 mL/kg about 4 h before, plus 3-5 mL/kg about 2 h before if no urine is produced or urine is very dark, and about 1.5 L per kg lost afterwards. DGE (2020) tolerates 2-4% losses, advises athletes to trust thirst, suggests drinking at most about 80% of sweat loss in long sessions, and says fluid is not needed for short sessions (30-40 min in its summary, up to 60 min in its main text).
**Grade:** moderate
**Applies to:** Evidence mostly from endurance exercise in young, often trained men. Short resistance sessions in a cool gym rarely reach 2%.
**Individual variation / conflicts:** Graded moderate because ACSM and DGE disagree: ACSM's 2% threshold versus DGE's 2-4% supports a range, not a sharp cut-off. ACSM's customised plans contrast with DGE's drink-to-thirst; both agree on avoiding large losses and weight gain.
**Sources:** [S377], [S378], [S803]

### Mild dehydration and strength
**Rule:** Treat starting a session clearly dehydrated (after a hot day, sauna, a hangover or a long fast with little fluid) as a likely few-percent drop in strength and rep capacity, fixed by normal drinking beforehand. Do not prescribe "hyper-hydration" or electrolyte products for ordinary gym sessions.
**Evidence:** A meta-analysis of 28 studies found hypohydration reduced strength by about 5.5%, muscular endurance by about 8.3% and anaerobic power by about 5.8%. Losses were larger with exercise-induced dehydration and smaller in trained people (P=0.06).
**Grade:** moderate
**Applies to:** Lab studies with deliberately induced dehydration; ordinary gym-goers drinking normally are unlikely to reach these levels.
**Individual variation / conflicts:** Water lost did not correlate with performance lost, so part of the effect may come from the heat or exercise used to dehydrate people.
**Sources:** [S379]

### Overdrinking and hyponatraemia
**Rule:** Never tell clients to drink as much as possible or on a fixed schedule regardless of thirst. In long events (over about 2-4 h, such as a first marathon or long hike), they should drink to thirst and must not finish heavier than they started. Headache, nausea, confusion or swelling after heavy drinking during a long event means seeking medical care, not drinking more water.
**Evidence:** The 2015 international consensus concluded that exercise-associated hyponatraemia (sodium below 135 mmol/L) is mainly caused by overdrinking low-sodium fluid, likely with water retention during exercise; prevention is drinking to thirst and not gaining weight. Sodium or sports drinks do not prevent it if a person overdrinks. In one Boston Marathon study, 13% of runners had hyponatraemia, mostly recreational runners slower than 4 hours.
**Grade:** strong
**Applies to:** Mainly prolonged endurance events, especially slow recreational finishers; very unlikely in gym sessions.
**Individual variation / conflicts:** Evidence is largely observational. An apparent higher risk in women disappeared after adjusting for BMI and race time. Older "drink before thirst" advice has been abandoned. One DGE author disclosed funding from the European Hydration Institute.
**Sources:** [S380], [S378]

### Sodium in long sessions and rehydration
**Rule:** Ordinary gym sessions under about 60-75 min need water only; normal meals replace sodium. Suggest a sodium-containing drink (about 400-1,100 mg/L) only for sessions over about 1-2 h, heavy sweating, heat or visible salt crusting. To rehydrate quickly before another session the same day, drink about 1.5 L per kg lost, sipped with salty food.
**Evidence:** ACSM (2007) says electrolyte and carbohydrate drinks can beat water in certain circumstances. DGE (2020) suggests 400-1,100 mg/L sodium and 4-8% carbohydrate for exercise over 60 min, sodium especially above 1.2 L/h sweat or 2 h duration, and 1.5 L per kg lost for fast rehydration; with losses under 5% and no session within 24 h, normal meals and drinks suffice.
**Grade:** moderate
**Applies to:** Endurance-athlete evidence. For recreational lifters on a diet, sports drinks mainly add sugar and energy.
**Individual variation / conflicts:** Sweat sodium varies widely. Clients on blood-pressure treatment or salt restriction should not add sodium drinks without medical advice. Recommended sodium ranges differ between bodies.
**Sources:** [S377], [S378]

### Salt limits
**Rule:** Target under 5 g salt a day (under 2 g sodium). Teach label reading: EU labels list salt, and salt = sodium × 2.5. Prioritise cutting cured meats, ready meals, savoury snacks, bread and cheese, and cooking at home. If using salt, use iodised salt.
**Evidence:** WHO strongly recommends adults eat less than 2 g sodium (5 g salt) a day; global average intake was about 4.3 g sodium (about 11 g salt) in 2019-2021. WHO and AESAN recommend iodised salt, and AESAN advises moderate cooking salt and lower-salt processed foods. EU law defines salt as sodium × 2.5.
**Grade:** strong
**Applies to:** General adult population. Heavy sweaters in long hot sessions may need extra sodium around training only.
**Individual variation / conflicts:** Some cohort studies report higher mortality at very low sodium intakes, which is contested (see "Salt reduction in normotensive people"). Spanish adults are far above 5 g, so the advice is directionally safe.
**Sources:** [S381], [S382], [S383], [S316]

### Salt reduction lowers blood pressure
**Rule:** Present salt reduction as a proven, dose-dependent way to lower blood pressure, especially for clients over about 45, with high-normal or high blood pressure, or a family history. The benefit builds over weeks. Pair it with weight loss, exercise and more fruit and vegetables, and never use it to replace prescribed medication.
**Evidence:** Cochrane (34 trials, 3,230 people): cutting salt by about 4.4 g/day lowered blood pressure by 4.18/2.06 mmHg (5.39/2.82 with hypertension, 2.42/1.00 without). A dose-response meta-analysis (133 trials, 12,197 people) found about -1.1 mmHg systolic per 50 mmol sodium reduction, larger in older, non-white and higher-blood-pressure groups; trials under 15 days showed less than half the effect.
**Grade:** strong
**Applies to:** Adults with or without hypertension, mostly middle-aged.
**Individual variation / conflicts:** Salt sensitivity varies; effects are small in young normotensive people. Heterogeneity between trials (I² 52-75%).
**Sources:** [S384], [S385]

### Salt reduction in normotensive people
**Rule:** Do not over-sell salt restriction to young, lean clients with normal blood pressure as a big health lever; frame it as moderate benefit, strongest with hypertension and older age. Do not push extreme restriction (well below about 1.5 g sodium) without medical supervision. The practical goal is to move from about 9-11 g towards 5 g of salt, not to zero.
**Evidence:** Graudal's Cochrane review found a large sodium cut lowered systolic pressure by only 1.14 mmHg in white normotensive participants (no diastolic change) versus -5.71/-2.87 mmHg in hypertension, and raised renin, aldosterone, noradrenaline and slightly cholesterol and triglycerides. The review's background (not its own analysis, which pooled RCTs on blood pressure, hormones and lipids) notes that recent cohort studies associate salt intake below 6 g with higher mortality.
**Grade:** moderate
**Applies to:** Mostly short-term RCTs with large sodium contrasts; the mortality concern is observational and is cited here second-hand from the review's background.
**Individual variation / conflicts:** Reviews disagree on the effect size in normotensive people (longer trials show more). The J-curve is disputed, and WHO keeps its strong <2 g sodium recommendation.
**Sources:** [S386]

### Potassium-enriched salt substitutes
**Rule:** If a client salts food, suggesting a potassium-enriched low-sodium salt is reasonable, but only after confirming no kidney disease and no potassium-sparing diuretics, ACE inhibitors/ARBs or potassium supplements; if unsure, refer to their GP. Do not suggest potassium tablets. Remind them that most salt in a Spanish or Western diet comes from processed and restaurant food.
**Evidence:** WHO (2025) conditionally recommends potassium-containing salt substitutes for adults who use table salt. Its review (26 RCTs, ~35,000 adults) found -4.76/-2.43 mmHg (moderate certainty). In SSaSS (20,995 high-risk older adults in rural China, 4.7 years), a 25% KCl substitute reduced stroke (0.86), major cardiovascular events (0.87) and death (0.88) without a significant rise in serious hyperkalaemia.
**Grade:** moderate
**Applies to:** Adults without kidney impairment, excluding pregnancy and children. Hard-outcome data come from older high-risk Chinese adults with high home salt use.
**Individual variation / conflicts:** WHO rated it conditional because overall certainty was low and undiagnosed potassium-excretion problems are possible. Hyperkalaemia data were sparse.
**Sources:** [S382], [S387]

## Alcohol

### No protective level of alcohol
**Rule:** Never recommend drinking for health ("a glass of wine is good for the heart" is not supported). Advise that less is better: for clients who drink, reduce frequency and amount and avoid binge sessions, respecting their choices without moralising. Refer suspected problem drinking to their GP.
**Evidence:** GBD 2016 found alcohol the 7th leading risk factor for deaths and DALYs (leading at ages 15-49), with zero drinks per week minimising health loss. WHO Europe (2023) states no safe amount for cancer can be established; light-to-moderate drinking was linked to almost 23,000 new EU cancers in 2017, and about half of alcohol-attributable cancers occur in non-heavy drinkers. A meta-analysis of 107 cohorts (4.8 million people), after bias correction, found no mortality benefit from low-volume drinking (RR 0.93, p=0.07) and higher risk at 45 g/day or more.
**Grade:** strong
**Applies to:** Adult general population; observational data.
**Individual variation / conflicts:** Zhao finds a null, not harmful, association at low volumes, while GBD and WHO conclude zero minimises risk, mainly through cancer. Absolute risk at very low intakes is small. Earlier J-curve findings are attributed to abstainer bias and comparison-group choice.
**Sources:** [S259], [S260], [S261], [S392]

### Spanish low-risk limits and binge drinking
**Rule:** Count alcohol in Spanish standard units (UBE, 10 g). Treat 2 UBE/day (men) and 1 UBE/day (women) as upper limits, not allowances, and recommend at least 2 alcohol-free days a week. Flag weekend binges (≥6 UBE men, ≥4 UBE women in one sitting) as a priority even when the weekly average looks low. Clients who are pregnant, breastfeeding, under 18, driving or on interacting medication should drink zero; for medication, have them check with their doctor or pharmacist. During fat loss, aim for as little as the client will sustainably accept.
**Evidence:** The Spanish Ministry of Health (2020) set low-risk limits of 20 g/day (men) and 10 g/day (women), stating "son límites de consumo, no objetivos a conseguir" and "Alcohol, cuanto menos mejor". One UBE is a 250 ml 5% caña, 125 ml 10% wine or a 30 ml 40% shot. It defines binge drinking as ≥60 g (men) or ≥40 g (women) in one occasion, says there is no safe level, and advises no alcohol when driving, pregnant, breastfeeding, under 18, caring for minors and with some medicines.
**Grade:** strong
**Applies to:** Adults in Spain. Other countries define standard drinks differently (14 g US, 8 g UK unit), so convert to grams.
**Individual variation / conflicts:** The sex split comes from the press release, not the leaflets. The ministry's clinical "risk criteria" (>4 UBE/day men, >2-2.5 women) are higher and should not be confused with the low-risk limits.
**Sources:** [S388], [S389], [S390], [S391]

### Energy content of alcohol
**Rule:** Log alcohol at 7 kcal/g (about 70 kcal per UBE) plus the drink's carbohydrate. Grams of alcohol = mL × %ABV × 0.789 / 100. Show clients the weekly total: 2 cañas a day is about 140 kcal of ethanol alone, roughly 1,000 kcal a week.
**Evidence:** EU labelling law sets the energy factor for ethanol at 29 kJ/g (7 kcal/g), versus 4 for carbohydrate and protein and 9 for fat.
**Grade:** strong
**Applies to:** Universal regulatory energy factor.
**Individual variation / conflicts:** Some alcohol energy may be lost as heat and metabolism may differ in heavy chronic drinkers; no source quantifying this was reviewed, so count the full 7 kcal/g.
**Sources:** [S316]

### Alcohol increases food intake
**Rule:** During fat loss, budget for the extra food as well as the drinks: expect a drinking occasion to add about 250+ kcal in total. Plan the meal before drinking, set a drink limit in advance, alternate with water or zero-alcohol drinks, keep high-protein, low-energy food available, and avoid drinking on an empty stomach late at night.
**Evidence:** A meta-analysis of 22 trials (701 adults) found people did not compensate for alcohol calories; alcohol increased food intake by about 82 kcal and total intake by about 256 kcal per occasion. An earlier lab meta-analysis found a large acute effect on food intake (d=1.03).
**Grade:** moderate
**Applies to:** Healthy adults mostly 18-37 in acute single-occasion lab studies.
**Individual variation / conflicts:** Substantial heterogeneity and small-study effects; some people eat less when drinking.
**Sources:** [S393], [S394]

### Alcohol and body weight
**Rule:** Do not claim any alcohol automatically causes weight gain, or that light drinking is harmless for fat loss. The calories and extra eating are real in the short term; heavy drinking (about 3+ UBE/day) and binges are linked to more abdominal fat in cross-sectional data; cutting alcohol is often one of the easiest ways to reduce calories. Judge it by the client's actual intake and pattern.
**Evidence:** A dose-response meta-analysis of 127 observational studies found no significant association with overweight or obesity in cohorts, but associations in cross-sectional studies (overweight/obesity OR 1.23, abdominal obesity OR 1.19). Heavy drinking (>28 g/day) was associated with higher odds of overweight/obesity (OR 1.32) and abdominal obesity (OR 1.25).
**Grade:** emerging
**Applies to:** Observational data from adults in mixed countries. Not for people with alcohol use disorder, who need referral.
**Individual variation / conflicts:** Cohort and cross-sectional results disagree, with confounding and self-reported intake. Popular advice outruns the evidence in both directions.
**Sources:** [S395]

### Alcohol after training
**Rule:** Advise against heavy drinking after hard training sessions, especially binge drinking, because it likely blunts recovery even when protein is eaten. Keep the post-training protein meal regardless. Do not claim one or two drinks measurably ruins gains; that has not been shown.
**Evidence:** In a randomised crossover in 8 active young men, 1.5 g/kg alcohol (about 10-11 Spanish standard units, UBE of 10 g, for a 70 kg person; the paper reports 12 ± 2 standard drinks for its participants) after combined resistance and interval exercise lowered myofibrillar protein synthesis by 24% with whey protein and 37% with carbohydrate, versus protein alone; synthesis still rose above rest in all conditions.
**Grade:** emerging
**Applies to:** Young active men, binge-level dose, one acute session, an 8-h surrogate outcome.
**Individual variation / conflicts:** Single small study; moderate doses, women, older adults and long-term outcomes are unstudied.
**Sources:** [S262]

## Energy availability, hormones and eating-disorder risk

### Low energy availability drives hormonal disruption
**Rule:** When dieting, avoid combining an aggressive deficit with high training volume, and keep carbohydrate adequate for the training load. Smaller deficits are safer, since no safe energy-availability cut-off is proven. Do not try to fix hormonal symptoms by changing fat percentage alone.
**Evidence:** The 2023 IOC REDs consensus identifies low energy availability (intake too low for exercise expenditure) as the cause of harm to health and performance in female and male exercisers, with an emerging role for low carbohydrate availability. In 35 sedentary ovulatory women aged 18-24 starting a diet-plus-exercise programme, odds of menstrual disturbance fell 9% per 1 kcal/kg FFM/day increase in energy availability (OR 0.91), roughly linearly across about 23-50 kcal/kg FFM/day with no clear threshold.
**Grade:** moderate
**Applies to:** Exercising adults of both sexes; the dose-response trial is a reasonable match for female gym beginners but does not cover men or older adults.
**Individual variation / conflicts:** The dose-response finding is a secondary analysis of one small trial. Susceptibility varies with individual moderating factors.
**Sources:** [S336], [S337]

### REDs: red flags and referral
**Rule:** Treat low energy availability as possible in anyone combining high training volume with restricted eating, men included. Watch for: loss of periods or irregular cycles, low libido or loss of morning erections, recurrent stress fractures or bone pain, frequent illness, persistent fatigue, falling performance despite training, and obsessive food or weight concerns. If any appear, stop increasing the deficit or training load and advise a sports-medicine physician. The coach does not diagnose REDs or run the clinical assessment tool, which needs blood tests and DXA.
**Evidence:** The IOC defines REDs as harmful health and performance outcomes in female and male athletes exposed to problematic low energy availability, and introduced a clinician traffic-light tool (CAT2). In 213 elite athletes, about 45% were flagged, with more amenorrhoea, bone stress injuries and lower T3, testosterone and BMD; orange status (OR 7.71) and low sex drive in males (OR 16.0) predicted later bone stress injury. A meta-analysis found low energy availability in 44.7% of athletes (44.2% female, 49.4% male), linked to impaired bone health.
**Grade:** moderate
**Applies to:** Elite and competitive athletes, mostly young; applying it to gym-goers is an extrapolation since prevalence and scoring are unvalidated there.
**Individual variation / conflicts:** Prevalence varies with how energy availability is estimated. Prospective injury data are self-reported with wide CIs. Whether a short, deliberate fat-loss phase counts as problematic is undefined.
**Sources:** [S336], [S346], [S347]

### No fixed energy-availability threshold
**Rule:** Do not calculate energy availability from app-logged intake and wearable expenditure and declare someone safe or unsafe against a 30 kcal/kg FFM cut-off. Use trends instead: persistent weight loss below a healthy range, menstrual changes, fatigue, cold intolerance and loss of libido. Any of these means referral, whatever the computed number says.
**Evidence:** The 2025 Female Athlete Triad Coalition update states that "the use of an EA threshold (e.g. < 30 kcal/kg FFM/day), is not recommended", because menstrual disturbances occur above it and energy availability is hard to estimate outside the lab and fluctuates daily. It uses several indicators (low or falling weight, reduced measured/predicted RMR, low T3, IGF-1 and leptin) and applies to physically active women, not only athletes.
**Grade:** moderate
**Applies to:** Women who exercise, from elite to physically active; less direct evidence for men and recreational lifters.
**Individual variation / conflicts:** Popular content still quotes 30 kcal/kg FFM as a hard line, as did older consensus documents.
**Sources:** [S348], [S337]

### Menstrual dysfunction: stop and refer
**Rule:** Ask women who diet or train hard about their cycle at the start and regularly, and about hormonal contraception, which masks it. Any new missed or irregular period during dieting or heavy training: ask about intake, recommend a GP visit and stop increasing the deficit. Periods absent for 3 months or more, or fewer than 6 a year: stop the deficit, move to maintenance or a small surplus (roughly +300-600 kcal/day), keep training moderate, and refer to a physician or gynaecologist/endocrinologist. Never present amenorrhoea as a sign of being lean enough.
**Evidence:** The 2025 Triad update lists no menses for more than 90 days or fewer than 6 in 12 months as high risk, and 6-9 a year as moderate risk. Functional hypothalamic amenorrhoea is a diagnosis of exclusion (pregnancy, PCOS, other endocrine causes, medication). An increase of 300-600 kcal/day may start recovery; in the 12-month REFUEL RCT, +330 kcal/day (+18%) improved regularity. Restored menses do not mean regular ovulation until several normal cycles occur.
**Grade:** moderate
**Applies to:** Premenopausal women who exercise (adult thresholds); not peri- or postmenopausal women.
**Individual variation / conflicts:** Cut-offs are risk-stratification criteria, not diagnoses; the first, lower tier (any new missed or irregular period) is a precautionary coaching trigger, not a source threshold. Recovery time varies with history, baseline status and psychosocial factors.
**Sources:** [S348]

### Very-low-fat diets and female hormones
**Rule:** Do not prescribe very-low-fat diets (below about 20% of energy) for women long term. Treat cycle changes (missed or late periods, much longer cycles) as a warning sign, usually caused by low energy availability rather than fat percentage, and respond by raising energy intake and referring.
**Evidence:** A 1999 meta-analysis of 13 studies found cutting fat lowered estradiol by 7.4% in premenopausal and 23.0% in postmenopausal women, largest at 10-12% of energy from fat. In one controlled-feeding study (n=30), moving from 40% to 20% fat lengthened the follicular phase (average 1.9 days in two-thirds of women). A 2025 meta-analysis of RCTs found no significant effect of low-fat diets on estradiol or progesterone (low certainty).
**Grade:** emerging
**Applies to:** Women in older, small studies, many designed for breast-cancer research rather than exercisers.
**Individual variation / conflicts:** The meta-analyses point in different directions; the follicular-phase study was non-randomised with a fixed order. Effects may be confounded by energy and fibre changes.
**Sources:** [S334], [S335], [S333]

### Low-fat diets and testosterone in men
**Rule:** Do not promise that adding fat will boost testosterone, or warn that moderate fat will crash it. Keep men at 20% of energy from fat or more as a precaution. If a male client reports low libido, fatigue or other low-testosterone symptoms during an aggressive cut, look first at the overall deficit, sleep and body-fat level, and refer rather than adjusting fat alone.
**Evidence:** Whittaker 2021 (6 studies, n=206 men) found lower total testosterone on low-fat diets (SMD -0.38). Soltani 2025 (11 RCTs, n=888, low fat ≤30% of energy) found no significant difference (low certainty).
**Grade:** emerging
**Applies to:** Mostly adult men in small trials; neither analysis studied trained people or energy deficits.
**Individual variation / conflicts:** Opposite conclusions; Whittaker 2021 has a corrigendum whose content could not be read. A small change within the normal range may not affect muscle gain.
**Sources:** [S332], [S333]

### Eating-disorder screening: brief questions as a prompt
**Rule:** There is no mandatory universal screening tool. At /setup, ask the five SCOFF-style questions as a prompt for a conversation, never as a diagnosis, and come back to them if warning signs appear. When an answer is partial or unclear, ask one clarifying question before counting it. A positive screen is 2 or more clear yes answers, the cut point the accuracy figures below were measured at; a single yes is noted but is not a positive screen. A positive screen or any warning sign ("Warning signs that warrant referral" in recovery-habits.md, such as self-induced vomiting or a rapid weight loss that worried the person or others) means the coach does not set a calorie deficit, weight targets or weigh-ins, and kindly recommends a GP or eating-disorder professional without labelling the person. A negative answer does not rule out an eating disorder, especially in men or with binge eating, so keep watching behaviour.
**Evidence:** In the USPSTF review (10 studies, n=3,684), SCOFF at a cut point of 2 or more had sensitivity 84% and specificity 80% in adults; another meta-analysis (25 studies) found 0.86 and 0.83. Sensitivity was lower with more men, binge-eating disorder and community samples.
**Grade:** moderate
**Applies to:** Adults, best validated in young women with anorexia or bulimia; uncertain in higher-weight people seeking weight loss.
**Individual variation / conflicts:** No study shows that screening itself improves outcomes, which is why the questions are a prompt rather than a mandatory screen. Kutz et al. find evidence insufficient for the full range of DSM-5 eating disorders in community settings.
**Sources:** [S349], [S350]

### Eating-disorder screen: EDE-QS
**Rule:** EDE-QS is optional, never mandatory, and can be used for repeated monitoring when a client agrees. Treat a score of ≥15 like any positive answer in "Eating-disorder screening: brief questions as a prompt": no deficit, weight targets or weigh-ins, and a referral conversation, never a diagnosis; most people above the cut-off do not have an eating disorder. A rising score during a diet is a reason to pause the deficit.
**Evidence:** EDE-QS is a 12-item, 7-day form validated in 559 adults (α=.913, test-retest ICC .93, r=.82-.91 with the full EDE-Q). A re-analysis proposed a cut-off of ≥15 (sensitivity .83, specificity .85, PPV .37), comparable to SCOFF.
**Grade:** emerging
**Applies to:** UK adults, about 81% female; not validated separately in men or people seeking weight loss.
**Individual variation / conflicts:** The cut-off comes from one re-analysis with self-reported eating-disorder status and no external validation. PPV is lower where eating disorders are rarer.
**Sources:** [S351], [S352]

### Calorie tracking and eating-disorder risk
**Rule:** Offer numeric calorie or macro tracking only to adults with no positive answer or warning sign on the brief eating-disorder questions, as optional and time-limited, with non-numeric alternatives (plate method, protein-per-meal targets, photo logs). Do not offer tracking or any weigh-ins to anyone with a positive answer or warning sign, a past eating disorder, or signs of compulsive tracking (distress at missing a log, rigid rules, compensatory exercise); drop numbers and refer.
**Evidence:** A review of 38 cross-sectional studies found diet and fitness app users, especially frequent users, had more disordered-eating symptoms. In the EAT cohort (n=1,446), app use was linked to disordered weight-control and muscle-building behaviours after adjusting for adolescent behaviour. A meta-analysis of general-population adults found no significant association (r=0.13; 9 studies, n=13,507), and two RCTs (1 month in 200 low-risk women; 12 months in 250 adults with BMI ≥27) found no harm. Among 105 people with a diagnosed eating disorder, 73% of MyFitnessPal users felt it contributed.
**Grade:** moderate
**Applies to:** Adults; reassurance applies to low-risk and supervised samples, harm signals to young adults and people with eating disorders.
**Individual variation / conflicts:** Reverse causation is plausible. Risk is concentrated in vulnerable individuals rather than the general population.
**Sources:** [S353], [S354], [S355], [S356], [S357], [S358]

## Medical situations and special populations

### Low- and very-low-calorie diets need clinical supervision
**Rule:** Never prescribe below about 1,200 kcal/day for women or 1,500 kcal/day for men without clinical supervision, and never prescribe total diet replacement. VLCD (<800 kcal/day) only under medical supervision. If the deficit maths points below the floor, or the client asks for a crash diet, refer to a GP or specialist weight-management service. Emphasise micronutrient-dense foods near the floor.
**Evidence:** NICE NG246 (2025) limits low-energy diets (800-1,200 kcal/day) to specialist or long-term-condition services, and very-low-energy diets (<800 kcal/day) to people with a clinical need for rapid loss, both nutritionally complete, at most 12 weeks, with clinical supervision and prior eating-disorder and medicines review. ADA 2025 restricts 800-1,000 kcal/day plans to carefully selected individuals in medical settings (electrolyte, fatigue and arrhythmia risks). A GLP-1 nutrition advisory notes micronutrient insufficiency is more likely below about 1,200 kcal/day (women) and 1,800 kcal/day (men).
**Grade:** strong
**Applies to:** Adults with overweight or obesity (UK and US guidelines); even more strongly to normal-weight people, who have no indication.
**Individual variation / conflicts:** Supervised programmes such as DiRECT work for type 2 diabetes remission, so the issue is supervision, not efficacy. Guideline labels differ. The 1,500 kcal/day male floor is pragmatic (the lower end of the AHA's 1,500-1,800 kcal/day dietary range for men in "Deficit size for weight loss"), not a supervision threshold from a guideline; the GLP-1 advisory's 1,800 kcal/day figure for men is a micronutrient-adequacy flag, not a floor.
**Sources:** [S359], [S360], [S361]

### Total diet replacement minimums
**Rule:** Use these figures only to recognise unsafe protocols: a homemade diet below 600 kcal/day, or a severely restricted plan with under about 75 g protein/day, falls short even of the minimum for medical formula products. Never build a TDR plan; it belongs with a clinician. Do not use the 30 g carbohydrate figure to judge ordinary low-carb diets with adequate energy.
**Evidence:** EFSA (2015) set TDR minimums of ≥600 kcal/day, ≥75 g protein, ≥30 g carbohydrate and micronutrients at reference values. Its 2021 statement removed the added linoleic acid requirement, set ALA at ≥0.8 g/day and kept total fat ≥20 g/day. EU Regulation 2017/1798 permits 600-1,200 kcal/day and a maximum of 8 weeks without medical supervision.
**Grade:** strong
**Applies to:** Formula TDR products for adults with overweight or obesity in the EU; a product standard, not dietary advice.
**Individual variation / conflicts:** Cite the 2021 fatty-acid values. NICE requires supervision for any diet of 1,200 kcal/day or less, stricter than the EU 8-week allowance.
**Sources:** [S362], [S363]

### Diabetes on insulin or sulfonylureas
**Rule:** If someone has type 1 diabetes, or type 2 treated with insulin or a sulfonylurea (gliclazide, glimepiride, glibenclamide and similar), do not start a deficit, low-carb or keto plan, fasting or a big jump in training until their diabetes clinician has reviewed doses. Give general habit support only, and tell them to report any hypoglycaemia symptoms. Also ask about blood-pressure medication, which may need reducing as weight falls.
**Evidence:** ADA 2025 says insulin and other diabetes medications may need adjusting with low-carbohydrate plans to prevent hypoglycaemia, and people on insulin or secretagogues need medical monitoring during fasting; it lists hypoglycaemia risk with GLP-1 RAs combined with insulin or sulfonylureas. NICE asks clinicians to review medicines before low-calorie diets. DiRECT withdrew antidiabetic and antihypertensive drugs at the start of its 825-853 kcal/day programme and excluded people on insulin.
**Grade:** moderate
**Applies to:** Adults with type 1 diabetes or type 2 on drugs that can cause hypoglycaemia. Metformin-only or diet-controlled type 2 carries lower risk, but the clinician should still be informed.
**Individual variation / conflicts:** No fixed dose-reduction protocol exists for weight-loss diets; ADA's percentage reductions come from fasting guidance and are not a general rule.
**Sources:** [S364], [S360], [S365], [S359]

### Chronic kidney disease
**Rule:** At onboarding, ask about kidney disease, low eGFR, protein in the urine, a kidney transplant, or diabetes or hypertension with known kidney involvement. With any diagnosed CKD, the protein target is set by the nephrologist or renal dietitian. Do not use the usual 1.6-2.2 g/kg/day protein targets, do not raise protein above general-population intake (about 0.8 g/kg/day) without clinician approval, and do not recommend creatine or protein supplements without that clinician's approval.
**Evidence:** For context only (not coach thresholds): KDIGO 2024 suggests 0.8 g/kg/day in CKD G3-G5 (grade 2C) and advises avoiding more than 1.3 g/kg/day in adults at risk of progression. Very-low-protein diets are only for willing adults under close supervision.
**Grade:** moderate
**Applies to:** Adults with diagnosed CKD; it does not show that high protein harms healthy kidneys.
**Individual variation / conflicts:** This overrides the muscle-building protein targets elsewhere in this file. The KDIGO recommendation is weak/low certainty and its 1.3 g/kg cap is a practice point, which is why the coach defers the number to the renal team instead of applying either figure.
**Sources:** [S366]

### Pregnancy
**Rule:** If a client is pregnant, switch off all deficit, fasting and very-low-carb programming, coach healthy eating and safe activity only, and leave any weight targets to their midwife or obstetrician. If a client is planning pregnancy, do not prescribe aggressive or very-low-carb cuts on your own initiative. If a GLP-1 or tirzepatide user is pregnant or planning pregnancy, tell them to contact their prescriber promptly.
**Evidence:** NICE NG247 (2025) advises that intentional weight loss in pregnancy is not recommended because of potential harm to the baby, with advice focused on healthy diet and activity. NICE NG246 says not to use semaglutide or tirzepatide in pregnancy, with contraception advice (tirzepatide users on oral contraception should switch or add a barrier method for 4 weeks after starting and after each dose increase). ADA 2025 does not recommend very-low-carbohydrate plans in pregnancy or lactation.
**Grade:** strong
**Applies to:** Pregnant people, and for the drug points people of childbearing potential on GLP-1 or tirzepatide. NG247 does not cover preconception.
**Individual variation / conflicts:** Clinicians may set gestational weight-gain limits for women with obesity; that is a clinical target, not a coach-prescribed deficit.
**Sources:** [S367], [S368], [S364]

### Breastfeeding
**Rule:** While breastfeeding: no aggressive cuts, VLCD, fasting or very-low-carb. Keep any deficit modest; about 500 kcal/day is the level studied, and treating it as a ceiling is a precaution. Wait until breastfeeding is well established, stop if milk supply, the baby's feeding or weight gain is affected, and involve the midwife, health visitor or GP.
**Evidence:** A 2026 review of 7 heterogeneous trials (11 days to 12 months) found a ~500 kcal/day restriction with macronutrient adjustment was associated with postpartum weight loss without self-reported effects on breastfeeding; effects on milk composition and the infant are unknown. ADA 2025 does not recommend very-low-carbohydrate plans during lactation.
**Grade:** emerging
**Applies to:** Breastfeeding adults postpartum; small, heterogeneous trials.
**Individual variation / conflicts:** Breastfeeding outcomes were self-reported. Milk supply responses vary.
**Sources:** [S369], [S364]

### Under-18s
**Rule:** Product policy based on the cited guidance (not a direct recommendation of these sources): users under 18 are out of scope of this template; refer them to a paediatric professional (paediatrician or paediatric dietitian). Meanwhile: no calorie targets, deficits, weigh-ins, body-fat goals or supplements beyond food. Coach only general habits (regular meals, protein and plants, sleep, enjoyable strength training and sport) and avoid talk about weight and body. Any weight management goes through a paediatric professional. If you notice signs of disordered eating, encourage them to talk to a parent or carer and their GP.
**Evidence:** The AAP (2016) notes some teenagers develop eating disorders while trying to lose weight and says the focus should be on healthy lifestyle rather than weight. NICE NG246 says dietary approaches for young people should focus on healthy eating rather than overly restrictive diets and should not be used alone outside a multicomponent intervention.
**Grade:** moderate
**Applies to:** Adolescents about 12-17; outside the target population, so this is a guardrail.
**Individual variation / conflicts:** NICE allows energy-controlled diets within clinician-led programmes, and the AAP says correctly conducted treatment does not raise eating-disorder risk. The coach's ban guards against unsupervised dieting. The AAP report dates from 2016.
**Sources:** [S370], [S359]

### GLP-1 and tirzepatide: lean-mass loss
**Rule:** Tell GLP-1 users that roughly a quarter to two-fifths of the weight lost may be lean tissue, similar to diet alone in the SURMOUNT-1 placebo arm. Relative body composition usually improves, but muscle and strength must be actively protected. Track strength and function (key lifts, grip, chair rise), not just weight, with extra attention for older adults and very fast losers.
**Evidence:** In the SURMOUNT-1 DXA substudy (n=160, 72 weeks), tirzepatide changed weight by -21.3%, fat by -33.9% and lean mass by -10.9%; about 75% of loss was fat in both tirzepatide and placebo arms. In STEP 1 (semaglutide), 62% of 13.6 kg lost was fat and 38% lean, roughly 20% muscle by the advisory's estimate. A 2026 meta-analysis (7 RCTs, 821 patients) found lean mass as a proportion of weight rose 1.81% while absolute lean mass fell 1.74 kg (I² 98%). Another 2026 meta-analysis rated the evidence low to very low certainty.
**Grade:** moderate
**Applies to:** Adults with obesity on obesity doses (SURMOUNT-1 mean BMI 38, 73% female). Older adults and people with low muscle are the main concern, with small post hoc subgroups.
**Individual variation / conflicts:** Laverde 2026 concludes lean loss should not be considered a limitation; Lopes Menezes 2026 cannot exclude clinically relevant loss in susceptible people. DXA lean mass includes water and organs. SURMOUNT-1 was manufacturer-funded and has an erratum that could not be checked.
**Sources:** [S371], [S361], [S372], [S373]

### GLP-1 users: protein, training and red flags
**Rule:** For GLP-1 or tirzepatide users, do not add a coach-imposed deficit on top of the drug; the prescribing clinician owns the weight plan, and this overrides the general deficit rules in this file. Coach progressive resistance training at least 3 times a week plus about 150 min of moderate cardio, and protein of about 1.2-1.6 g/kg/day or 80-120 g/day unless the clinician says otherwise (based on adjusted or fat-free mass for people with high body weight), spread over small meals that suit the reduced appetite. If intake drops below about 1,200 kcal (women) or 1,800 kcal (men), the advisory's micronutrient-adequacy flag, emphasise nutrient-dense foods and suggest they discuss supplements and monitoring with their prescriber. Screen for eating-disorder risk. Refer back to the prescriber for persistent vomiting, very low intake, dizziness, signs of a restrictive eating disorder, very rapid weight loss or pregnancy plans. Never advise on dose changes.
**Evidence:** A 2025 joint advisory (ACLM, ASN, OMA, TOS) recommends strength training ≥3×/week plus ≥150 min/week aerobic activity; notes 1.2-1.6 g/kg/day, ~1.5 g/kg FFM or 80-120 g/day as proposed targets, not below 0.4-0.5 g/kg/day and avoiding prolonged ≥2 g/kg/day; warns about micronutrients below 1,200/1,800 kcal; calls for eating-disorder screening and states restrictive eating disorder is a general contraindication. ADA 2025 says incretin therapies may increase malnutrition and sarcopenia risk.
**Grade:** moderate
**Applies to:** Adults with obesity on GLP-1-based therapy, especially older adults and those with low strength. Protein may need lowering in CKD (see "Chronic kidney disease").
**Individual variation / conflicts:** The no-extra-deficit rule is a coach inference, not stated in the sources. No RCT yet shows a specific protein dose plus training preserves muscle on GLP-1 therapy; a 2025 Delphi consensus says its recommendations are mainly indirect. No consensus on which body mass to base protein on. The advisory's caution about ≥2 g/kg is below some sports targets.
**Sources:** [S361], [S374], [S360]

## Conflicts and open questions

- **Best RMR equation in obesity:** Mifflin is the most precise, but WHO, Henry or Harris-Benedict are less biased in BMI ≥40, and Harris-Benedict showed the smallest bias during weight loss. [S161], [S162], [S163], [S268]
- **Cunningham in trained people:** unbiased on average across athletes but overestimating under best-practice testing and underestimating in collegiate athletes; heterogeneity is very high. [S165], [S270], [S271]
- **Activity multipliers:** app steps (1.2, 1.375, 1.55, 1.725) are convention, not validated against DLW; self-reported activity is noisy rather than consistently inflated, contrary to popular advice. [S166], [S281], [S284], [S285], [S286]
- **Constrained versus additive energy expenditure:** whether exercise compensation works through lower REE or through less non-exercise activity is unresolved. [S281], [S282], [S283]
- **"Rapid loss burns muscle":** not supported for FFM in people with overweight; in lean trained people slower rates are recommended on weaker evidence. [S168], [S170]
- **Metabolic damage and diet breaks:** adaptive thermogenesis is modest and partly reversible; claims that diet breaks or refeeds "reset metabolism" or "boost leptin" outrun the evidence, and diet-break trials disagree with each other. [S171], [S172], [S178], [S179], [S180], [S181]
- **Protein plateau:** Morton finds a plateau around 1.6 g/kg (wide CI, non-significant), Tagawa a small continued benefit up to 3.5 g/kg; both agree the effect is small. Several key authors have industry ties. [S186], [S187], [S188]
- **Older-adult protein:** EFSA keeps 0.83 g/kg for all ages, while PROT-AGE, ESPEN and some national bodies recommend 1.0-1.5 g/kg. [S795], [S192], [S193], [S194]
- **Per-meal protein ceiling:** the 20-30 g per meal idea conflicts with newer tracer data showing 100 g gives a larger, longer response. [S196], [S197]
- **Upper protein intake:** EFSA's "safe" ~1.7 g/kg sits below common sports targets; this is a data gap, not proof of harm. In diagnosed CKD the renal team sets protein, overriding sports targets. [S199], [S200], [S366]
- **Plant versus animal protein:** meta-analyses disagree on a small advantage for animal protein in adults under 50. [S202], [S203], [S241]
- **Carbohydrate for lifters:** ISSN's 5-8 g/kg/day for "active individuals" conflicts with resistance-training evidence showing no benefit above general intakes in most sessions. [S326], [S327]
- **Fat and sex hormones:** two meta-analyses on testosterone, and two on estradiol, reach opposite conclusions. [S332], [S333], [S334]
- **Time-restricted eating:** meta-analyses disagree on extra weight loss versus isocaloric controls and on lean-mass loss. [S226], [S228], [S229], [S230], [S231], [S232], [S233], [S234], [S235]
- **Ultra-processed foods:** whether processing itself matters or only energy density and ingredients is disputed; AESAN attributes harm to ingredients. [S342], [S343], [S344], [S340]
- **Free sugars:** RCTs support causal links with obesity and dyslipidaemia, while cohorts show no relationship in isocaloric exchange; WHO gives numbers, EFSA only "as low as possible". [S338], [S339], [S341]
- **Salt in normotensive people and very low sodium:** effect size is small in young normotensive people, and a J-curve for mortality is reported in cohorts but disputed. [S384], [S385], [S386]
- **Light drinking:** a null mortality association at low volumes (Zhao) versus "zero minimises risk" (GBD, WHO); older protective findings are attributed to bias. Alcohol and weight associations differ between cohort and cross-sectional studies. [S259], [S260], [S261], [S392], [S395]
- **Logging and sex:** some sources find women under-report more on recalls, others find no consistent sex difference. [S289], [S295], [S296], [S299]
- **App validity:** MyFitnessPal is accurate for energy after cleaning in one study and poor in others, depending on entries chosen. [S307], [S310], [S311]
- **Energy-availability threshold:** the old 30 kcal/kg FFM line is no longer recommended. [S337], [S348]
- **Tracking and eating disorders:** cross-sectional and cohort associations versus null meta-analysis and RCTs in low-risk samples. [S353], [S354], [S355], [S356], [S357]
- **GLP-1 lean-mass loss:** interpretations range from "not a limitation" to "cannot exclude clinically relevant loss". [S371], [S372], [S373]
- **Hydration thresholds:** ACSM's 2% versus DGE's 2-4%, and customised drinking plans versus drinking to thirst. [S377], [S378], [S380]
- **Popular claims that outrun the evidence:** the 3500 kcal rule for long-term forecasts, "1 g protein per lb for everyone dieting", genotype-based diet choice, "insulin magic" for low-carb, "sugar is toxic regardless of calories", fat burners and BCAAs, fish-oil capsules for general health, and vitamin D megadoses. [S159], [S292], [S190], [S210], [S216], [S341], [S256], [S258], [S254], [S252]

## When to refer out

Stop prescribing numbers and refer to the appropriate clinician when any of these apply:

- Any positive answer to the brief eating-disorder questions or a warning sign (including EDE-QS ≥15 if used), a past eating disorder, or signs of compulsive tracking or loss-of-control eating. [S349], [S351], [S358]
- Any new missed or irregular period (GP visit; refer and stop the deficit at 3+ months or fewer than 6 a year), low libido, recurrent stress fractures, persistent fatigue or falling performance during a diet. [S336], [S348]
- The plan points below about 1,200 kcal/day (women) or 1,500 kcal/day (men), a crash diet, VLCD or total diet replacement. [S359], [S360], [S363]
- Type 1 diabetes, or type 2 on insulin or sulfonylureas, before any deficit, low-carb, fasting or big training change. [S364]
- Any diagnosed kidney disease, low eGFR or kidney involvement: the renal team sets protein; refer before raising protein or adding creatine. [S366], [S247]
- Pregnancy, breastfeeding concerns, or pregnancy plans on GLP-1 or tirzepatide. [S367], [S368], [S369]
- Any user under 18 (out of scope; paediatric professional). [S359], [S370]
- GLP-1 users with persistent vomiting, very low intake, dizziness or very rapid weight loss. [S361]
- Obesity with comorbidities or complex medical needs (registered dietitian). [S212]
- Unintentional weight loss in older adults, dizziness or confusion, or diuretic use. [S280], [S376]
- Suspected problem drinking. [S259], [S389]
- Potassium salt substitutes for anyone with kidney disease or potassium-affecting medication; any change to prescribed vitamin D, omega-3 or blood-pressure treatment. [S382], [S252], [S254]
