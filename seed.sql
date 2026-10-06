USE placement_db;

INSERT INTO students (name, email, branch, cgpa, backlogs, skills) VALUES
('Sainath Shinde','sainath@example.com','MCA',8.41,0,'C++,Python,SQL,DSA,OOP'),
('Amit Patil','amit@example.com','MCA',7.20,0,'Java,SQL,Python'),
('Neha Kulkarni','neha@example.com','MCA',9.05,0,'Python,ML,SQL,Pandas'),
('Rohan More','rohan@example.com','MCA',6.40,1,'C,C++'),
('Pooja Jadhav','pooja@example.com','MCA',8.10,0,'Java,Spring,SQL');

INSERT INTO companies (name, industry, location) VALUES
('TCS','IT Services','Pune'),
('Infosys','IT Services','Bengaluru'),
('Persistent Systems','Product','Pune'),
('DataNova Analytics','Data/AI','Hyderabad');

INSERT INTO jobs (company_id,title,package_lpa,min_cgpa,max_backlogs,required_skills,deadline,status) VALUES
(1,'Graduate Software Engineer',3.60,6.00,1,'Java,SQL','2030-12-31','OPEN'),
(2,'Systems Engineer',4.00,6.50,0,'Python,SQL','2030-12-31','OPEN'),
(3,'Software Engineer',7.50,8.00,0,'C++,DSA,OOP','2030-12-31','OPEN'),
(4,'ML Engineer Trainee',6.00,7.50,0,'Python,ML,Pandas','2030-12-31','OPEN');