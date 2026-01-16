<?php
    include "config.php";
    $ids =[];
    $get_id_query="select req_id from student_registration_requests";
    $result=mysqli_query($conn,$get_id_query);
    while($row=mysqli_fetch_array($result)){
        array_push($ids,$row["req_id"]);
    }
    $approved= [];
    $denied= [];

    foreach($ids as $id){
        $id_str="id_".$id;
        $str=$_POST[$id_str];
        if($str== "approved"){
            array_push($approved,$id);
        }else if($str== "denied"){
            array_push($denied,$id);
        }
    }

    if(count($approved)>0){
        $get_info="select * from student_registration_requests where";
        $insertstudentinfo="insert into students(Registration_number,full_name,faculty,email) values ";
        $add_user="insert into users(userName,passwd,role,status,active) values ";
        $ids=" ";
        for($i=0;$i<count($approved); $i++){
            $id=$approved[$i];
            if($i== 0){
                $ids.= "req_id=$id";
            }else{
                $ids.= " or req_id=$id";
            }
        }
        $get_info.=$ids.";";
        $result=$conn->query($get_info);
        while($row=mysqli_fetch_array($result)){
            $reg_no=$row["Registration_number"];
            $full_name=$row["firstName"]." ".$row["lastName"];
            $faculty=$row["Faculty"];
            $email=$row["email"];
            $passwd_hash=$row["passwd"];
            $insertstudentinfo.="('$reg_no','$full_name','$faculty','$email'),";
            $add_user.="('$reg_no','$passwd_hash','student','active','yes'),";
        }
        $insertstudentinfo[strlen($insertstudentinfo)-1]= ";";
        $add_user[strlen($add_user)-1]= ";";

        $conn->query($insertstudentinfo);
        $conn->query($add_user);
    }

    foreach($approved as $id){
        array_push($denied,$id);
    }

    if(count($denied)> 0){
        $reject_sql="delete from student_registration_requests where";
        $reject_ids= " ";
        for($i=0;$i<count($denied); $i++){
            $id=$denied[$i];
            if($i== 0){
                $id=$denied[$i];
                $reject_ids.= "req_id=$id";
            }else{
                $reject_ids.= " or req_id=$id";
            }
        }
        $reject_ids.=";";
        $reject_sql.=$reject_ids;
        $sql_rejected_images="select id_img_name from student_registration_requests where";
        $sql_rejected_images.=$reject_ids;
        
        $result=$conn->query($sql_rejected_images);
        while($row=mysqli_fetch_assoc($result)){
            $file_name=$row["id_img_name"];
            if(file_exists("../uplodes/register_id_pics/".$file_name)){
                unlink("../uplodes/register_id_pics/".$file_name);
            }
        }        
        $conn->query($reject_sql);
        header("Location: ../dashbords/requests.php");
        exit();
    }

    
    
?>