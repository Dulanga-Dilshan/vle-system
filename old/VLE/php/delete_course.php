<?php
session_start();
if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
    header("Location: ../index.php");
    exit;
}
include "../php/config.php";
$id=trim($_POST["id"]);

$sql= "delete from courses where course_id=?; ";
$stmnt=$conn->prepare($sql);
$stmnt->bind_param("i",$id);
$stmnt->execute();
if($stmnt->affected_rows > 0){
    header("Location: ../dashbords/managecourses.php?delete_status=true");
    exit;
}else{
    header("Location: ../dashbords/managecourses.php?delete_status=failed");
    exit;
}