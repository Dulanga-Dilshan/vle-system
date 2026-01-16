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
$id=trim($_POST["id"]);

$update_course_sql= "
    update courses set
    course_code=?, course_name=?,faculty=?,lecture_in_charge=?
    where course_id=?;
";

$stmnt=$conn->prepare($update_course_sql);
$stmnt->bind_param("sssii",$course_code,$course_name,$faculty,$lecture, $id);
$stmnt->execute();
if($stmnt->affected_rows > 0){
    header("Location: ../dashbords/managecourses.php?update_status=true");
    exit;
}else{
    header("Location: ../dashbords/managecourses.php?update_status=failed");
    exit;
}
