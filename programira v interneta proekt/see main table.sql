SELECT week1.start_time, week1.end_time, week1.day_of_week, rooms.room_number, specializations.name_specialization, 
class_groups.number_group, subjects.name_subject, subject_type.type_subject, lecturers.name_person, week1.id 
FROM week1
JOIN rooms ON rooms.id = week1.room_id
JOIN specializations ON specializations.id = week1.specialization_id
JOIN class_groups ON class_groups.id = week1.group_id
JOIN subjects ON subjects.id = week1.subject_id
JOIN subject_type ON subject_type.id = week1.subject_type_id
JOIN lecturers ON lecturers.id = week1.lecturer_id