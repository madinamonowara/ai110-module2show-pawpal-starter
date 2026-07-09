# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
3 core actions:
- add/manage pet care tasks 
- update todays contraints (only have 30 min this evening)
- generate daily plans

- What classes did you include, and what responsibilities did you assign to each?

The 4 classes:

Class 1: Pet
Class 1 Attributes: 
    name, species, age, weight, activityLevel, medicalNeeds
Class 1 Methods:    
    displayProfile(), updateInfo(), getCareRequirements()

Class 2: CareTask
Class 2 Attributes:
    taskName, type (feeding, walk, meds, grooming), priority, duration, frequency, dueTime, completed
Class 2 Methods:
    markComplete(), markIncomplete(), isOverdue(), updateTask()

Class 3: OwnerPreferences
Class 3: Attributes: 
    availableTime, busyHours, preferredTaskTimes, dailyTimeLimit, taskPreferences
Class 3: Methods:
    updateAvailability(), updatePreferences(), isAvailable(time)

Class 4: PetCareAssistant
Class 4: Attributes: 
    pets, tasks, ownerPreferences, dailyPlan
Class 4: Methods:
    generateDailyPlan(), prioritizeTasks(), explainPlan(), rescheduleTasks()


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, took scheduler out from PetCareAssistant so the scheduling algorithm is testable on a plain list of tasks.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler detects overlapping tasks and auto-resolves them by shifting the lower-priority task to the next open slot, and reporting each move rather than reordering silently. 

The tradeoff: right now the system isnt able to honor "must happen by" deadlines. To keep the logic more simpler I thought this was fine since these tasks would most likely get labled higher prioirty anyways, but this would be a natural next step. 


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
