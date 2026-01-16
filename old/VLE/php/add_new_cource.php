<?php
session_start();
if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
    header("Location: ../index.php");
    exit;
}
include "../php/config.php";
$course_code=trim($_POST["course_code"]);
$course_name=trim($_POST["course_name"]);
$faculty=trim($_POST["faculty"]);
$lecture=trim($_POST["lecturer"]);

$check_course_code="
    select * from courses where course_code=?;
";

$check_stmnt=$conn->prepare($check_course_code);
$check_stmnt->bind_param("s", $course_code);
$check_stmnt->execute();
$result=$check_stmnt->get_result();
if($result->num_rows > 0){
    header("Location: ../dashbords/managecourses.php?insert_status=coures_exsists");
    exit;
}

$sql="
    insert into courses(course_code,course_name,faculty,lecture_in_charge) values(?,?,?,?);
";

$stmnt=$conn->prepare($sql);
$stmnt->bind_param("sssi", $course_code,$course_name, $faculty, $lecture);
$stmnt->execute();
if($stmnt->affected_rows > 0){
    header("Location: ../dashbords/managecourses.php?insert_status=true");
    exit;
}else{
    header("Location: ../dashbords/managecourses.php?incert_status=failed");
    exit;
}