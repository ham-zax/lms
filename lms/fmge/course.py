"""Shared installer for reviewed multi-section PSM courses."""

import json

import frappe
from frappe import _

from lms.fmge.importer import _load_bank, import_bank
from lms.lms.utils import get_editorjs_blocks, get_lms_route


SECTION_WORDS = {2: "two", 3: "three", 4: "four", 5: "five"}


class PSMCourse:
	def __init__(self, day: int, section_count: int = 2):
		self.day = day
		self.section_count = section_count
		self.section_numbers = tuple(range(1, section_count + 1))
		self.course_name = f"fmge-psm-day-{day}"
		self.course_title = f"FMGE PSM Day {day}"
		self.chapter_title = f"Day {day} PSM Practice"
		self.quiz_title = f"FMGE PSM Day {day} Mock"
		self.quiz_name = f"fmge-psm-day-{day}-mock"
		self.bank_id = f"fmge-psm-day{day}"
		self.bank_file = f"psm_day{day}.json"
		self.source_pdf_url = f"/assets/lms/fmge/day{day}-psm-notes.pdf"
		self.mock_url = f"/lms/fmge/day{day}/mock"

	def section(self, section=1):
		"""Resolve only the fixed sections; never accept caller-provided bank IDs."""
		if isinstance(section, bool) or str(section) not in {str(n) for n in self.section_numbers}:
			frappe.throw(
				_("Choose a section from 1 to {0}.").format(self.section_count), frappe.ValidationError
			)
		return self._section_spec(int(section))

	def _section_spec(self, number):
		return {
			"number": number,
			"bank_id": self.bank_id if number == 1 else f"{self.bank_id}-section-2",
			"bank_file": self.bank_file if number == 1 else f"psm_day{self.day}_section_2.json",
			"quiz_name": self.quiz_name if number == 1 else f"fmge-psm-day-{self.day}-section-2",
			"quiz_title": self.quiz_title if number == 1 else f"FMGE PSM Day {self.day} Section 2",
			"mock_url": self.mock_url if number == 1 else f"{self.mock_url}?section=2",
		}

	@property
	def question_count(self):
		return len(_load_bank(self.section(1)["bank_file"])["questions"])

	@property
	def total_question_count(self):
		return sum(len(_load_bank(self.section(n)["bank_file"])["questions"]) for n in self.section_numbers)

	@property
	def section_words(self):
		return SECTION_WORDS.get(self.section_count, str(self.section_count))

	@property
	def short_introduction(self):
		return (
			f"{self.total_question_count} reviewed Community Medicine questions in "
			f"{self.section_words} Day {self.day} sections."
		)

	@property
	def description(self):
		links = "".join(
			f'<p><a href="{self.section(n)["mock_url"]}">Take section {n} without signing in</a></p>'
			for n in self.section_numbers
		)
		return (
			links
			+ f"<p>Revise Community Medicine with {self.total_question_count} reviewed questions from the "
			f"Day {self.day} notes in {self.section_words} sections. Choose untimed practice with immediate feedback "
			"or a timed mock with one minute per question. Results include teaching explanations "
			"and links to the source pages.</p>"
			f'<p><a href="{self.source_pdf_url}">Open the Day {self.day} PSM reference PDF</a></p>'
		)

	def _course(self, owner):
		if frappe.db.exists("LMS Course", self.course_name):
			course = frappe.get_doc("LMS Course", self.course_name)
			if course.title != self.course_title:
				frappe.throw(
					_("The Day {0} course name belongs to another course.").format(self.day),
					frappe.ValidationError,
				)
			if course.short_introduction != self.short_introduction or course.description != self.description:
				course.short_introduction = self.short_introduction
				course.description = self.description
				course.save(ignore_permissions=True)
			return course
		course = frappe.new_doc("LMS Course")
		course.title = self.course_title
		course.short_introduction = self.short_introduction
		course.description = self.description
		course.append("instructors", {"instructor": owner})
		course.insert(ignore_permissions=True, set_name=self.course_name)
		return course

	def _chapter(self, course):
		linked = [row.chapter for row in course.chapters]
		matching = frappe.get_all(
			"Course Chapter", filters={"course": course.name, "title": self.chapter_title}, pluck="name"
		)
		if matching:
			if len(matching) != 1 or linked != matching:
				frappe.throw(
					_("The Day {0} course has an unexpected chapter layout.").format(self.day),
					frappe.ValidationError,
				)
			return frappe.get_doc("Course Chapter", matching[0])
		if linked:
			frappe.throw(
				_("The Day {0} course already has a different chapter.").format(self.day),
				frappe.ValidationError,
			)
		chapter = frappe.new_doc("Course Chapter")
		chapter.title = self.chapter_title
		chapter.course = course.name
		chapter.insert(ignore_permissions=True)
		course.reload()
		course.append("chapters", {"chapter": chapter.name})
		course.save(ignore_permissions=True)
		return chapter

	def _lesson(self, quiz, chapter, section):
		linked = [row.lesson for row in chapter.lessons]
		if quiz.lesson:
			lesson = frappe.get_doc("Course Lesson", quiz.lesson)
			if (
				lesson.course != chapter.course
				or lesson.chapter != chapter.name
				or len(linked) > self.section_count
				or len(linked) < section["number"]
				or linked[section["number"] - 1] != lesson.name
				or not any(
					block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz.name
					for block in get_editorjs_blocks(lesson.content)
				)
			):
				frappe.throw(
					_("The Day {0} quiz is linked to an unexpected lesson.").format(self.day),
					frappe.ValidationError,
				)
			return lesson
		if len(linked) != section["number"] - 1 or quiz.course:
			frappe.throw(
				_("The Day {0} course already has a different lesson.").format(self.day),
				frappe.ValidationError,
			)
		lesson = frappe.new_doc("Course Lesson")
		lesson.title = section["quiz_title"]
		lesson.chapter = chapter.name
		lesson.content = json.dumps(
			{
				"blocks": [
					{
						"id": f"fmgeday{self.day}section{section['number']}",
						"type": "quiz",
						"data": {"quiz": quiz.name},
					}
				],
				"version": "2.29.0",
			}
		)
		lesson.insert(ignore_permissions=True)
		chapter.append("lessons", {"lesson": lesson.name})
		chapter.save(ignore_permissions=True)
		return lesson

	def _source_sections(self):
		sections = []
		all_ids = set()
		for number in self.section_numbers:
			section = self.section(number)
			bank = _load_bank(section["bank_file"])
			ids = [item["id"] for item in bank["questions"]]
			count = len(ids)
			if (
				bank["bank_id"] != section["bank_id"]
				or bank["title"] != section["quiz_title"]
				or not 1 <= count <= 50
				or int(bank.get("expected_questions", count)) != count
				or int(bank.get("duration_minutes", 0)) != count
				or len(set(ids)) != count
				or all_ids.intersection(ids)
			):
				frappe.throw(
					_("The source sections have invalid metadata or overlapping IDs."), frappe.ValidationError
				)
			all_ids.update(ids)
			sections.append({**section, "ids": ids, "count": count})
		return sections

	def _prepare_chapter(self, chapter, sections):
		"""Hook for courses that must migrate an earlier lesson layout."""

	def install(self):
		"""Reconcile every section bank and preserve existing section lessons."""
		sections = self._source_sections()
		course = None
		for section in sections:
			result = import_bank(section["bank_file"])
			if result["quiz"] != section["quiz_name"]:
				frappe.throw(_("The imported section has an unexpected quiz name."), frappe.ValidationError)
			quiz = frappe.get_doc("LMS Quiz", result["quiz"])
			if course is None:
				course = self._course(quiz.owner)
				chapter = self._chapter(course)
				self._prepare_chapter(chapter, sections)
			self._lesson(quiz, chapter, section)
		if not course.published:
			course.reload()
			course.published = 1
			course.save(ignore_permissions=True)
		return self.verify()

	def verify(self):
		"""Check every section lesson, its settings and all ordered source IDs."""
		sections = self._source_sections()
		course = frappe.get_doc("LMS Course", self.course_name)
		if not course.published or course.title != self.course_title or len(course.chapters) != 1:
			frappe.throw(_("The course must be published with one chapter."), frappe.ValidationError)
		chapter = frappe.get_doc("Course Chapter", course.chapters[0].chapter)
		if chapter.course != course.name or chapter.title != self.chapter_title or len(chapter.lessons) != self.section_count:
			frappe.throw(
				_("The course must contain exactly {0} section lessons.").format(self.section_count),
				frappe.ValidationError,
			)
		results = []
		for index, section in enumerate(sections):
			lesson = frappe.get_doc("Course Lesson", chapter.lessons[index].lesson)
			quiz = frappe.get_doc("LMS Quiz", section["quiz_name"])
			if (
				quiz.course != course.name
				or quiz.lesson != lesson.name
				or quiz.fmge_bank_id != section["bank_id"]
				or lesson.course != course.name
				or lesson.chapter != chapter.name
				or lesson.title != section["quiz_title"]
				or quiz.title != section["quiz_title"]
				or int(quiz.duration) != section["count"]
				or int(quiz.total_marks) != section["count"]
				or quiz.show_answers
				or quiz.enable_negative_marking
				or section["mock_url"] not in (course.description or "")
				or not any(
					block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz.name
					for block in get_editorjs_blocks(lesson.content)
				)
			):
				frappe.throw(_("A section is not configured or linked correctly."), frappe.ValidationError)
			actual = [
				frappe.db.get_value("LMS Question", row.question, "fmge_question_id")
				for row in quiz.questions
			]
			if actual != section["ids"]:
				frappe.throw(_("A section does not match its source bank."), frappe.ValidationError)
			results.append(
				{
					"section": section["number"],
					"quiz": quiz.name,
					"lesson": lesson.name,
					"questions": len(actual),
					"duration_minutes": int(quiz.duration),
					"mock_url": section["mock_url"],
				}
			)
		return {
			"course": course.name,
			"course_url": get_lms_route(f"courses/{course.name}"),
			"mock_url": get_lms_route(f"fmge/day{self.day}/mock"),
			"published": bool(course.published),
			"lesson": results[0]["lesson"],
			"questions": results[0]["questions"],
			"duration_minutes": results[0]["duration_minutes"],
			"total_questions": sum(row["questions"] for row in results),
			"sections": results,
		}
