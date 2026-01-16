<?php
    include "config.php";
    $ids =[];
    $get_id_query="select id from staff_registration_requests";
    $result=mysqli_query($conn,$get_id_query);
    while($row=mysqli_fetch_array($result)){
        array_push($ids,$row["id"]);
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

    if(count($approved)> 0){
        if(count($approved)>0){
            $get_info="select * from staff_registration_requests where";
            $insertstaffinfo="insert into staff(staff_id,full_name,email,sub_role) values ";
            $add_user="insert into users(userName,passwd,role,status,active) values ";
            $ids=" ";
            for($i=0;$i<count($approved); $i++){
                $id=$approved[$i];
                if($i== 0){
                    $ids.= "id=$id";
                }else{
                    $ids.= " or id=$id";
                }
            }
        }
    
        $get_info.=$ids.";";
        $result=$conn->query($get_info);
        while($row=mysqli_fetch_array($result)){
            $staff_id=$row["staff_id"];
            $full_name=$row["full_name"];
            $role=$row["sub_role"];
            $email=$row["email"];
            $passwd_hash=$row["passwd"];

            $insertstaffinfo.="('$staff_id','$full_name','$email','$role'),";
            $add_user.="('$staff_id','$passwd_hash','staff','active','no'),";
        }
        $insertstaffinfo[strlen($insertstaffinfo)-1]= ";";
        $add_user[strlen($add_user)-1]= ";";

        $conn->query($insertstaffinfo);
        $conn->query($add_user);
    }

    foreach($approved as $id){
        array_push($denied,$id);
    }

    if(count($denied)> 0){
        $reject_sql="delete from staff_registration_requests where";
        $reject_ids= " ";
        for($i=0;$i<count($denied); $i++){
            $id=$denied[$i];
            if($i== 0){
                $id=$denied[$i];
                $reject_ids.= "id=$id";
            }else{
                $reject_ids.= " or id=$id";
            }
        }
        $reject_ids.=";";
        $reject_sql.=$reject_ids;

        echo $reject_sql;
        
        $conn->query($reject_sql);
        header("Location: ../dashbords/requests.php");
        exit();
    }
