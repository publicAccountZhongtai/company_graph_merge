  <?php

//接收表单数据
$user = $_POST['user'];

//数据库连接语句, 参数包含:服务器地址,用户名,登录密码,数据库名称,默认端口)
$db = new mysqli('localhost','root','','0104test','3306');
//判断是否成功连接数据库
if (mysqli_connect_error()) {
    echo '0';
    exit();
}
//设置数据库查询数据编码格式 (相当重要) 如果不设置从数据库查出来的数据就是乱码
$db->query("SET NAMES UTF8");
//查询语句
$sql = "select * from t_user WHERE uname = \"$user\"";
//echo $sql;

//执行查询语句
$result = $db->query($sql);

//执行 fetch_assoc()函数
$na = $result->fetch_assoc();
//判断用户名是否存在
if ($na == null){
    echo'1';
}else{
    echo '0';
}
?>