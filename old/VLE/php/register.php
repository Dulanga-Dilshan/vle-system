<?php
    include "config.php";
    $register_id_pic_path="../uplodes/register_id_pics/";
    $date=date('Y-m-d');
    
    if($_SERVER["REQUEST_METHOD"] == "POST"){
        $role=$_POST["role"];
        if($role== null){die("dscsdcd"); }
        if($role== "student"){
            $fname=trim($_POST["fname"]);
            $lname=trim($_POST["lname"]);
            $reg_no=trim($_POST["registerNO"]);

            $result=$conn->query("select id from users where userName='$reg_no'");
            if($result->num_rows > 0){
                header("Location: ../dashbords/registation.php?user_name_error=1");
                exit();
            }

            $faculty=trim($_POST["faculty"]);
            $email=trim($_POST["email"]);
            $password=trim($_POST["passwd"]);
            $passwd=password_hash($password, PASSWORD_DEFAULT);

            $file=$_FILES["idImg"];
            $file_ex=explode(".",$file["name"]);
            $file_ex=strtolower(end($file_ex));
            $file_size=$file['size'];
            $allowedExtensions = ['jpg', 'jpeg', 'png', 'gif'];
            $date=date('Y-m-d');

            if($file_size<1024*1024*5){
                if(in_array($file_ex, $allowedExtensions)){
                    $file_new_name=uniqid($reg_no."_",true).".".$file_ex;
                    if(!move_uploaded_file($file['tmp_name'], $register_id_pic_path.$file_new_name)){
                        $_SESSION['register_img_err']="failed_while_saving";
                        $file_new_name="missing";
                    }
                }else{
                    $_SESSION['register_img_err']="file_not_allowed";
                    $file_new_name= "missing";
                }
            }else{
                $_SESSION['register_img_err']="too_large_file: ".$file_size;
                $file_new_name= "missing";
            }

            $sql = "insert into student_registration_requests(firstName,lastName,Registration_number,Faculty,id_img_name, email,passwd,req_date)
                    values(?,?,?,?,?,?,?,?)";

            $stmt= $conn->prepare($sql);
            $stmt->bind_param("ssssssss",$fname,$lname,$reg_no,$faculty,$file_new_name,$email,$passwd,$date);
            $stmt->execute();
            $stmt->close();
        }else{
            $full_name=trim($_POST["staffName"]);
            $id=trim($_POST["staffID"]);
            $sub_role=trim($_POST["staffType"]);
            $email=trim($_POST["email"]);
            $password=trim($_POST["passwd"]);
            $passwd=password_hash($password, PASSWORD_DEFAULT);

            $result=$conn->query("select id from users where userName='$id'");
            if($result->num_rows > 0){
                header("Location: ../dashbords/registation.php?user_name_error=1");
                exit();
            }

            $sql="
                insert into staff_registration_requests(staff_id,full_name,sub_role,email,passwd,req_date) 
                values(?,?,?,?,?,?)";

            $stmt= $conn->prepare($sql);
            $stmt->bind_param("ssssss",$id,$full_name,$sub_role,$email,$passwd, $date);
            $stmt->execute();
            $stmt->close();
        }
        $_SESSION["register_status"]="true";
        header("Location: ../dashbords/register.html");
        exit();






    }
?>