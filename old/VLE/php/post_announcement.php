<?php
session_start();
if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
    header("Location: ../index.php");
    exit;
}
include "../php/config.php";

$target_str="";
$audience_type = $_POST["audience_type"];
$title =trim($_POST["title"]);
$message=trim($_POST["message"]);
$date=date('Y-m-d');


if($audience_type=="all"){
    $target_str = "all";
}else{
    $group=$_POST["group"];
    if($group== "students"){
        $target_str = "students_";
        $student_year = $_POST["student_year"];
        $target_str.=$student_year;
        $faculty = $_POST["student_faculty"];
        $target_str.="_";
        $target_str.=$faculty;
    }elseif($group== "staff"){
        $target_str = "staff_";
        $staff_type = $_POST["staff_type"];
        $faculty = $_POST["staff_faculty"];
        $target_str.=$staff_type;
        $target_str.= "_";
        $target_str.= $faculty;
    }else if($group== "faculty"){
        $target_str="faculty_";
        $faculty=$_POST["faculty"];
        $target_str.= $faculty;
    }
}

$sql="insert into Announcements(Title,Message,target_audience,announcement_date) values(?,?,?,?);";
$stmnt=$conn->prepare($sql);
$stmnt->bind_param("ssss",$title,$message,$target_str,$date);
$stmnt->execute();
if($stmnt->affected_rows > 0){
    header("Location: ../dashbords/anousment.php?announcement_status=true");
    exit;
}else{
    header("Location: ../dashbords/anousment.php?announcement_status=failed");
    exit;
}