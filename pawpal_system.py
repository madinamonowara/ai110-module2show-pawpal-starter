from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Pet:
	name: str
	species: str
	age: int
	weight: float
	activityLevel: str
	medicalNeeds: List[str] = field(default_factory=list)

	def displayProfile(self) -> str:
		pass

	def updateInfo(self) -> None:
		pass

	def getCareRequirements(self) -> List[str]:
		pass


@dataclass
class CareTask:
	taskName: str
	type: str
	priority: str
	duration: int
	frequency: str
	dueTime: datetime
	completed: bool = False
	pet: Pet | None = None

	def markComplete(self) -> None:
		pass

	def markIncomplete(self) -> None:
		pass

	def isOverdue(self) -> bool:
		pass

	def updateTask(self) -> None:
		pass


@dataclass
class OwnerPreferences:
	availableTime: int
	busyHours: List[str] = field(default_factory=list)
	preferredTaskTimes: List[str] = field(default_factory=list)
	dailyTimeLimit: int = 0
	taskPreferences: List[str] = field(default_factory=list)

	def updateAvailability(self) -> None:
		pass

	def updatePreferences(self) -> None:
		pass

	def isAvailable(self, time: datetime) -> bool:
		pass


@dataclass
class PetCareAssistant:
	pets: List[Pet] = field(default_factory=list)
	tasks: List[CareTask] = field(default_factory=list)
	ownerPreferences: OwnerPreferences | None = None
	dailyPlan: List[CareTask] = field(default_factory=list)

	def generateDailyPlan(self) -> List[CareTask]:
		pass

	def prioritizeTasks(self) -> List[CareTask]:
		pass

	def explainPlan(self) -> str:
		pass

	def rescheduleTasks(self) -> None:
		pass
