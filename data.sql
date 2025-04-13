-- Create Credentials table
CREATE TABLE Credentials (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('customer', 'owner', 'admin'))
);


-- Create Customer table
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    FOREIGN KEY (username) REFERENCES Credentials(username) ON DELETE CASCADE
);


-- Create HomeOwner table
CREATE TABLE HomeOwner (
    owner_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    address TEXT,
    verification_status VARCHAR(20) NOT NULL CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    FOREIGN KEY (username) REFERENCES Credentials(username) ON DELETE CASCADE
);


-- Create Property table
CREATE TABLE Property (
    property_id INT PRIMARY KEY,
    owner_id INT NOT NULL,
    admin_username VARCHAR(50),
    property_type VARCHAR(50) NOT NULL CHECK (property_type IN ('apartment', 'house', 'condo', 'villa', 'room')),
    sale_renting VARCHAR(50) NOT NULL CHECK (sale_renting IN ('sale', 'rent')),
    cost INT NOT NULL,
    building VARCHAR(100),
    street VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    pin VARCHAR(20) NOT NULL,
    area DECIMAL(10,2) NOT NULL,
    rent DECIMAL(10,2) NOT NULL,
    description TEXT,
    amenities TEXT,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    sharing_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    coord_X DECIMAL(9,6),
    coord_Y DECIMAL(9,6),
    FOREIGN KEY (owner_id) REFERENCES HomeOwner(owner_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_username) REFERENCES Credentials(username) ON DELETE CASCADE
);

-- Create SharedRoom table
CREATE TABLE SharedRoom (
    room_id INT PRIMARY KEY,
    property_id INT NOT NULL,
    monthly_rent DECIMAL(10,2) NOT NULL,
    total_beds INT NOT NULL CHECK (total_beds > 0),
    available_beds INT NOT NULL CHECK (available_beds >= 0),
    description TEXT,
    FOREIGN KEY (property_id) REFERENCES Property(property_id) ON DELETE CASCADE,
    CHECK (available_beds <= total_beds)
);

-- Create Receipt table
CREATE TABLE Receipt (
    receipt_id INT PRIMARY KEY,
    property_id INT NOT NULL,
    customer_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_date DATE NOT NULL,
    FOREIGN KEY (property_id) REFERENCES Property(property_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE
);

-- Create Buy_Rent relationship table
CREATE TABLE Buy_Rent (
    customer_id INT,
    property_id INT,
    PRIMARY KEY (customer_id, property_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES Property(property_id) ON DELETE CASCADE
);

-- Create Interested_In_Sharing relationship table
CREATE TABLE Interested_In_Sharing (
    customer_id INT,
    room_id INT,
    PRIMARY KEY (customer_id, room_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES SharedRoom(room_id) ON DELETE CASCADE
);


-- Create Participates relationship table
CREATE TABLE Participates (
    customer_id INT,
    room_id INT,
    PRIMARY KEY (customer_id, room_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES SharedRoom(room_id) ON DELETE CASCADE
);

-- Insert into Credentials (50 customers, 10 admins, 30 homeowners)
INSERT INTO Credentials (username, password, user_type) VALUES
-- Customers (50)
('john.doe', 'pass123', 'customer'), ('jane.smith', 'pass456', 'customer'), ('mike.wilson', 'pass789', 'customer'),
('emily.brown', 'pass101', 'customer'), ('david.jones', 'pass202', 'customer'), ('sarah.taylor', 'pass303', 'customer'),
('chris.evans', 'pass404', 'customer'), ('laura.martin', 'pass505', 'customer'), ('peter.parker', 'pass606', 'customer'),
('lisa.jackson', 'pass707', 'customer'), ('tom.hardy', 'pass808', 'customer'), ('amy.white', 'pass909', 'customer'),
('robert.king', 'pass010', 'customer'), ('julia.roberts', 'pass111', 'customer'), ('mark.twain', 'pass222', 'customer'),
('kate.winslet', 'pass333', 'customer'), ('steve.jobs', 'pass444', 'customer'), ('anna.miller', 'pass555', 'customer'),
('ben.franklin', 'pass666', 'customer'), ('clara.barton', 'pass777', 'customer'), ('daniel.craig', 'pass888', 'customer'),
('emma.watson', 'pass999', 'customer'), ('frank.sinatra', 'pass000', 'customer'), ('grace.kelly', 'pass121', 'customer'),
('harry.potter', 'pass232', 'customer'), ('irene.adler', 'pass343', 'customer'), ('jack.sparrow', 'pass454', 'customer'),
('karen.page', 'pass565', 'customer'), ('leo.dicaprio', 'pass676', 'customer'), ('mia.wallace', 'pass787', 'customer'),
('nina.simone', 'pass898', 'customer'), ('oliver.queen', 'pass909', 'customer'), ('penny.lane', 'pass010', 'customer'),
('quinn.fabray', 'pass121', 'customer'), ('rachel.green', 'pass232', 'customer'), ('sam.wilson', 'pass343', 'customer'),
('tina.fey', 'pass454', 'customer'), ('uma.thurman', 'pass565', 'customer'), ('victor.hugo', 'pass676', 'customer'),
('wendy.williams', 'pass787', 'customer'), ('xander.harris', 'pass898', 'customer'), ('yolanda.smith', 'pass909', 'customer'),
('zach.taylor', 'pass010', 'customer'), ('alice.cooper', 'pass121', 'customer'), ('bob.marley', 'pass232', 'customer'),
('carol.danvers', 'pass343', 'customer'), ('diana.prince', 'pass454', 'customer'), ('eddie.murphy', 'pass565', 'customer'),
('fiona.apple', 'pass676', 'customer'), ('george.lucas', 'pass787', 'customer'),
-- Admins (10)
('admin.alex', 'admin001', 'admin'), ('admin.beth', 'admin002', 'admin'), ('admin.carl', 'admin003', 'admin'),
('admin.dana', 'admin004', 'admin'), ('admin.eric', 'admin005', 'admin'), ('admin.faye', 'admin006', 'admin'),
('admin.gina', 'admin007', 'admin'), ('admin.hank', 'admin008', 'admin'), ('admin.iris', 'admin009', 'admin'),
('admin.jake', 'admin010', 'admin'),
-- Homeowners (30)
('owner.tom', 'owner001', 'owner'), ('owner.lily', 'owner002', 'owner'), ('owner.paul', 'owner003', 'owner'),
('owner.rose', 'owner004', 'owner'), ('owner.jack', 'owner005', 'owner'), ('owner.mary', 'owner006', 'owner'),
('owner.nick', 'owner007', 'owner'), ('owner.sue', 'owner008', 'owner'), ('owner.kim', 'owner009', 'owner'),
('owner.lee', 'owner010', 'owner'), ('owner.bob', 'owner011', 'owner'), ('owner.amy', 'owner012', 'owner'),
('owner.joe', 'owner013', 'owner'), ('owner.eva', 'owner014', 'owner'), ('owner.ian', 'owner015', 'owner'),
('owner.zoe', 'owner016', 'owner'), ('owner.max', 'owner017', 'owner'), ('owner.ada', 'owner018', 'owner'),
('owner.eli', 'owner019', 'owner'), ('owner.uma', 'owner020', 'owner'), ('owner.vin', 'owner021', 'owner'),
('owner.wes', 'owner022', 'owner'), ('owner.xia', 'owner023', 'owner'), ('owner.yan', 'owner024', 'owner'),
('owner.zac', 'owner025', 'owner'), ('owner.ben', 'owner026', 'owner'), ('owner.cia', 'owner027', 'owner'),
('owner.dan', 'owner028', 'owner'), ('owner.fay', 'owner029', 'owner'), ('owner.gil', 'owner030', 'owner');

-- Insert into Customer (50 customers)
INSERT INTO Customer (customer_id, username, first_name, last_name, email, phone) VALUES
(1, 'john.doe', 'John', 'Doe', 'john.doe@email.com', '123-456-7890'),
(2, 'jane.smith', 'Jane', 'Smith', 'jane.smith@email.com', '234-567-8901'),
(3, 'mike.wilson', 'Mike', 'Wilson', 'mike.wilson@email.com', '345-678-9012'),
(4, 'emily.brown', 'Emily', 'Brown', 'emily.brown@email.com', '456-789-0123'),
(5, 'david.jones', 'David', 'Jones', 'david.jones@email.com', '567-890-1234'),
(6, 'sarah.taylor', 'Sarah', 'Taylor', 'sarah.taylor@email.com', '678-901-2345'),
(7, 'chris.evans', 'Chris', 'Evans', 'chris.evans@email.com', '789-012-3456'),
(8, 'laura.martin', 'Laura', 'Martin', 'laura.martin@email.com', '890-123-4567'),
(9, 'peter.parker', 'Peter', 'Parker', 'peter.parker@email.com', '901-234-5678'),
(10, 'lisa.jackson', 'Lisa', 'Jackson', 'lisa.jackson@email.com', '012-345-6789'),
(11, 'tom.hardy', 'Tom', 'Hardy', 'tom.hardy@email.com', '123-456-7891'),
(12, 'amy.white', 'Amy', 'White', 'amy.white@email.com', '234-567-8902'),
(13, 'robert.king', 'Robert', 'King', 'robert.king@email.com', '345-678-9013'),
(14, 'julia.roberts', 'Julia', 'Roberts', 'julia.roberts@email.com', '456-789-0124'),
(15, 'mark.twain', 'Mark', 'Twain', 'mark.twain@email.com', '567-890-1235'),
(16, 'kate.winslet', 'Kate', 'Winslet', 'kate.winslet@email.com', '678-901-2346'),
(17, 'steve.jobs', 'Steve', 'Jobs', 'steve.jobs@email.com', '789-012-3457'),
(18, 'anna.miller', 'Anna', 'Miller', 'anna.miller@email.com', '890-123-4568'),
(19, 'ben.franklin', 'Ben', 'Franklin', 'ben.franklin@email.com', '901-234-5679'),
(20, 'clara.barton', 'Clara', 'Barton', 'clara.barton@email.com', '012-345-6790'),
(21, 'daniel.craig', 'Daniel', 'Craig', 'daniel.craig@email.com', '123-456-7892'),
(22, 'emma.watson', 'Emma', 'Watson', 'emma.watson@email.com', '234-567-8903'),
(23, 'frank.sinatra', 'Frank', 'Sinatra', 'frank.sinatra@email.com', '345-678-9014'),
(24, 'grace.kelly', 'Grace', 'Kelly', 'grace.kelly@email.com', '456-789-0125'),
(25, 'harry.potter', 'Harry', 'Potter', 'harry.potter@email.com', '567-890-1236'),
(26, 'irene.adler', 'Irene', 'Adler', 'irene.adler@email.com', '678-901-2347'),
(27, 'jack.sparrow', 'Jack', 'Sparrow', 'jack.sparrow@email.com', '789-012-3458'),
(28, 'karen.page', 'Karen', 'Page', 'karen.page@email.com', '890-123-4569'),
(29, 'leo.dicaprio', 'Leo', 'DiCaprio', 'leo.dicaprio@email.com', '901-234-5680'),
(30, 'mia.wallace', 'Mia', 'Wallace', 'mia.wallace@email.com', '012-345-6791'),
(31, 'nina.simone', 'Nina', 'Simone', 'nina.simone@email.com', '123-456-7893'),
(32, 'oliver.queen', 'Oliver', 'Queen', 'oliver.queen@email.com', '234-567-8904'),
(33, 'penny.lane', 'Penny', 'Lane', 'penny.lane@email.com', '345-678-9015'),
(34, 'quinn.fabray', 'Quinn', 'Fabray', 'quinn.fabray@email.com', '456-789-0126'),
(35, 'rachel.green', 'Rachel', 'Green', 'rachel.green@email.com', '567-890-1237'),
(36, 'sam.wilson', 'Sam', 'Wilson', 'sam.wilson@email.com', '678-901-2348'),
(37, 'tina.fey', 'Tina', 'Fey', 'tina.fey@email.com', '789-012-3459'),
(38, 'uma.thurman', 'Uma', 'Thurman', 'uma.thurman@email.com', '890-123-4570'),
(39, 'victor.hugo', 'Victor', 'Hugo', 'victor.hugo@email.com', '901-234-5681'),
(40, 'wendy.williams', 'Wendy', 'Williams', 'wendy.williams@email.com', '012-345-6792'),
(41, 'xander.harris', 'Xander', 'Harris', 'xander.harris@email.com', '123-456-7894'),
(42, 'yolanda.smith', 'Yolanda', 'Smith', 'yolanda.smith@email.com', '234-567-8905'),
(43, 'zach.taylor', 'Zach', 'Taylor', 'zach.taylor@email.com', '345-678-9016'),
(44, 'alice.cooper', 'Alice', 'Cooper', 'alice.cooper@email.com', '456-789-0127'),
(45, 'bob.marley', 'Bob', 'Marley', 'bob.marley@email.com', '567-890-1238'),
(46, 'carol.danvers', 'Carol', 'Danvers', 'carol.danvers@email.com', '678-901-2349'),
(47, 'diana.prince', 'Diana', 'Prince', 'diana.prince@email.com', '789-012-3460'),
(48, 'eddie.murphy', 'Eddie', 'Murphy', 'eddie.murphy@email.com', '890-123-4571'),
(49, 'fiona.apple', 'Fiona', 'Apple', 'fiona.apple@email.com', '901-234-5682'),
(50, 'george.lucas', 'George', 'Lucas', 'george.lucas@email.com', '012-345-6793');

-- Insert into HomeOwner (30 homeowners)
INSERT INTO HomeOwner (owner_id, username, first_name, last_name, email, phone_number, address, verification_status) VALUES
(1, 'owner.tom', 'Tom', 'Hanks', 'tom.hanks@email.com', '123-456-7800', '123 Oak St, Los Angeles, CA', 'verified'),
(2, 'owner.lily', 'Lily', 'James', 'lily.james@email.com', '234-567-8900', '456 Pine St, San Diego, CA', 'pending'),
(3, 'owner.paul', 'Paul', 'Walker', 'paul.walker@email.com', '345-678-9000', '789 Maple Ave, San Francisco, CA', 'verified'),
(4, 'owner.rose', 'Rose', 'Byrne', 'rose.byrne@email.com', '456-789-0100', '101 Elm St, Seattle, WA', 'verified'),
(5, 'owner.jack', 'Jack', 'Black', 'jack.black@email.com', '567-890-1200', '202 Birch Rd, Portland, OR', 'rejected'),
(6, 'owner.mary', 'Mary', 'Jones', 'mary.jones@email.com', '678-901-2300', '303 Cedar Ln, Denver, CO', 'verified'),
(7, 'owner.nick', 'Nick', 'Cage', 'nick.cage@email.com', '789-012-3400', '404 Spruce Dr, Austin, TX', 'pending'),
(8, 'owner.sue', 'Sue', 'Ellen', 'sue.ellen@email.com', '890-123-4500', '505 Willow Way, Houston, TX', 'verified'),
(9, 'owner.kim', 'Kim', 'Lee', 'kim.lee@email.com', '901-234-5600', '606 Ash St, Dallas, TX', 'verified'),
(10, 'owner.lee', 'Lee', 'Smith', 'lee.smith@email.com', '012-345-6700', '707 Poplar Ave, Miami, FL', 'pending'),
(11, 'owner.bob', 'Bob', 'Dylan', 'bob.dylan@email.com', '123-456-7801', '808 Magnolia Dr, Orlando, FL', 'verified'),
(12, 'owner.amy', 'Amy', 'Adams', 'amy.adams@email.com', '234-567-8902', '909 Palm St, Tampa, FL', 'verified'),
(13, 'owner.joe', 'Joe', 'Pesci', 'joe.pesci@email.com', '345-678-9003', '1010 Cherry Ln, Atlanta, GA', 'verified'),
(14, 'owner.eva', 'Eva', 'Green', 'eva.green@email.com', '456-789-0104', '1111 Peach Rd, Charlotte, NC', 'pending'),
(15, 'owner.ian', 'Ian', 'Fleming', 'ian.fleming@email.com', '567-890-1205', '1212 Plum St, Raleigh, NC', 'verified'),
(16, 'owner.zoe', 'Zoe', 'Saldana', 'zoe.saldana@email.com', '678-901-2306', '1313 Vine St, Boston, MA', 'verified'),
(17, 'owner.max', 'Max', 'Payne', 'max.payne@email.com', '789-012-3407', '1414 Ivy Ln, New York, NY', 'pending'),
(18, 'owner.ada', 'Ada', 'Lovelace', 'ada.lovelace@email.com', '890-123-4508', '1515 Oakwood Dr, Philadelphia, PA', 'verified'),
(19, 'owner.eli', 'Eli', 'Roth', 'eli.roth@email.com', '901-234-5609', '1616 Pinewood Ave, Chicago, IL', 'verified'),
(20, 'owner.uma', 'Uma', 'Thurman', 'uma.thurman@email.com', '012-345-6710', '1717 Maplewood St, Detroit, MI', 'verified'),
(21, 'owner.vin', 'Vin', 'Diesel', 'vin.diesel@email.com', '123-456-7811', '1818 Elmwood Rd, Cleveland, OH', 'pending'),
(22, 'owner.wes', 'Wes', 'Anderson', 'wes.anderson@email.com', '234-567-8909', '1919 Birchwood Ln, Columbus, OH', 'verified'),
(23, 'owner.xia', 'Xia', 'Li', 'xia.li@email.com', '345-678-9010', '2020 Cedarwood Dr, Phoenix, AZ', 'verified'),
(24, 'owner.yan', 'Yan', 'Chen', 'yan.chen@email.com', '456-789-0111', '2121 Sprucewood Ave, Tucson, AZ', 'pending'),
(25, 'owner.zac', 'Zac', 'Efron', 'zac.efron@email.com', '567-890-1212', '2222 Willowwood St, Las Vegas, NV', 'verified'),
(26, 'owner.ben', 'Ben', 'Affleck', 'ben.affleck@email.com', '678-901-2313', '2323 Ashwood Rd, Salt Lake City, UT', 'verified'),
(27, 'owner.cia', 'Cia', 'Bella', 'cia.bella@email.com', '789-012-3414', '2424 Poplarwood Ln, Boise, ID', 'pending'),
(28, 'owner.dan', 'Dan', 'Brown', 'dan.brown@email.com', '890-123-4515', '2525 Magnoliawood Dr, Helena, MT', 'verified'),
(29, 'owner.fay', 'Fay', 'Wray', 'fay.wray@email.com', '901-234-5616', '2626 Palmwood Ave, Billings, MT', 'verified'),
(30, 'owner.gil', 'Gil', 'Scott', 'gil.scott@email.com', '012-345-6717', '2727 Cherrywood St, Anchorage, AK', 'verified');

-- Insert into Property (30 properties)
INSERT INTO Property (property_id, owner_id, admin_username, property_type, sale_renting, cost, building, street, city, pin, area, rent, description, amenities, is_available, sharing_allowed, coord_X, coord_Y) VALUES
(1, 1, 'admin.alex', 'apartment', 'rent', 1200, 'Sunset Towers', '123 Sunset Blvd', 'Los Angeles', '90001', 800.50, 1200.00, 'Cozy apartment with a view', 'Pool, Gym', TRUE, FALSE, 34.0522, -118.2437),
(2, 2, 'admin.beth', 'house', 'sale', 250000, NULL, '456 Ocean Dr', 'San Diego', '92101', 1500.00, 0.00, 'Spacious family home', 'Garage, Garden', TRUE, FALSE, 32.7157, -117.1611),
(3, 3, 'admin.carl', 'condo', 'rent', 1800, 'Bayview Condos', '789 Bay St', 'San Francisco', '94102', 1000.75, 1800.00, 'Modern condo near downtown', 'Parking, Balcony', TRUE, FALSE, 37.7749, -122.4194),
(4, 4, 'admin.dana', 'villa', 'sale', 500000, NULL, '101 Lake Rd', 'Seattle', '98101', 2000.25, 0.00, 'Luxury villa with lake view', 'Pool, Sauna', TRUE, FALSE, 47.6062, -122.3321),
(5, 5, 'admin.eric', 'room', 'rent', 600, 'Green Apartments', '202 Forest St', 'Portland', '97201', 300.00, 600.00, 'Single room for rent', 'Shared Kitchen', TRUE, TRUE, 45.5152, -122.6784),
(6, 6, 'admin.faye', 'house', 'sale', 300000, NULL, '303 Mountain Dr', 'Denver', '80201', 1800.50, 0.00, 'Mountain retreat home', 'Fireplace, Deck', TRUE, FALSE, 39.7392, -104.9903),
(7, 7, 'admin.gina', 'apartment', 'rent', 1500, 'City Heights', '404 Central Ave', 'Austin', '73301', 900.25, 1500.00, 'Urban apartment', 'Gym, Rooftop', TRUE, FALSE, 30.2672, -97.7431),
(8, 8, 'admin.hank', 'condo', 'sale', 200000, 'Riverfront Condos', '505 River Rd', 'Houston', '77002', 1100.00, 0.00, 'Condo with river view', 'Pool, Security', TRUE, FALSE, 29.7604, -95.3698),
(9, 9, 'admin.iris', 'villa', 'rent', 2500, NULL, '606 Hill St', 'Dallas', '75201', 2200.75, 2500.00, 'Spacious villa', 'Garden, Pool', TRUE, FALSE, 32.7767, -96.7970),
(10, 10, 'admin.jake', 'room', 'rent', 700, 'Palm Apartments', '707 Palm Dr', 'Miami', '33101', 350.50, 700.00, 'Shared room available', 'Shared Bath', TRUE, TRUE, 25.7617, -80.1918),
(11, 11, 'admin.alex', 'house', 'sale', 275000, NULL, '808 Magnolia Ln', 'Orlando', '32801', 1600.00, 0.00, 'Family home near park', 'Garage, Patio', TRUE, FALSE, 28.5383, -81.3792),
(12, 12, 'admin.beth', 'apartment', 'rent', 1300, 'Skyline Towers', '909 Skyline Dr', 'Tampa', '33601', 850.25, 1300.00, 'Downtown apartment', 'Gym, Parking', TRUE, FALSE, 27.9506, -82.4572),
(13, 13, 'admin.carl', 'condo', 'sale', 220000, 'Peach Condos', '1010 Peach St', 'Atlanta', '30301', 1200.50, 0.00, 'Modern condo', 'Balcony, Security', TRUE, FALSE, 33.7490, -84.3880),
(14, 14, 'admin.dana', 'villa', 'rent', 2800, NULL, '1111 Lakeview Rd', 'Charlotte', '28201', 2300.75, 2800.00, 'Luxury villa', 'Pool, Deck', TRUE, FALSE, 35.2271, -80.8431),
(15, 15, 'admin.eric', 'room', 'rent', 650, 'Plum Apartments', '1212 Plum St', 'Raleigh', '27601', 320.00, 650.00, 'Single room', 'Shared Kitchen', TRUE, TRUE, 35.7796, -78.6382),
(16, 16, 'admin.faye', 'house', 'sale', 350000, NULL, '1313 Vine Dr', 'Boston', '02108', 1900.25, 0.00, 'Historic home', 'Fireplace, Garden', TRUE, FALSE, 42.3601, -71.0589),
(17, 17, 'admin.gina', 'apartment', 'rent', 2000, 'Ivy Towers', '1414 Ivy Ln', 'New York', '10001', 950.50, 2000.00, 'Luxury apartment', 'Gym, Doorman', TRUE, FALSE, 40.7128, -74.0060),
(18, 18, 'admin.hank', 'condo', 'sale', 240000, 'Oakwood Condos', '1515 Oakwood Dr', 'Philadelphia', '19102', 1300.75, 0.00, 'Spacious condo', 'Parking, Balcony', TRUE, FALSE, 39.9526, -75.1652),
(19, 19, 'admin.iris', 'villa', 'rent', 2700, NULL, '1616 Pinewood Ave', 'Chicago', '60601', 2100.00, 2700.00, 'Modern villa', 'Pool, Sauna', TRUE, FALSE, 41.8781, -87.6298),
(20, 20, 'admin.jake', 'room', 'rent', 800, 'Maple Apartments', '1717 Maple St', 'Detroit', '48201', 400.25, 800.00, 'Shared room', 'Shared Bath', TRUE, TRUE, 42.3314, -83.0458),
(21, 21, 'admin.alex', 'house', 'sale', 310000, NULL, '1818 Elmwood Rd', 'Cleveland', '44101', 1700.50, 0.00, 'Family home', 'Garage, Deck', TRUE, FALSE, 41.4993, -81.6944),
(22, 22, 'admin.beth', 'apartment', 'rent', 1400, 'Birch Towers', '1919 Birch Ln', 'Columbus', '43201', 875.75, 1400.00, 'Cozy apartment', 'Gym, Parking', TRUE, FALSE, 39.9612, -82.9988),
(23, 23, 'admin.carl', 'condo', 'sale', 230000, 'Cedar Condos', '2020 Cedar Dr', 'Phoenix', '85001', 1150.00, 0.00, 'Modern condo', 'Balcony, Pool', TRUE, FALSE, 33.4484, -112.0740),
(24, 24, 'admin.dana', 'villa', 'rent', 2600, NULL, '2121 Spruce St', 'Tucson', '85701', 2050.25, 2600.00, 'Spacious villa', 'Garden, Pool', TRUE, FALSE, 32.2226, -110.9747),
(25, 25, 'admin.eric', 'room', 'rent', 750, 'Willow Apartments', '2222 Willow Dr', 'Las Vegas', '89101', 375.50, 750.00, 'Single room', 'Shared Kitchen', TRUE, TRUE, 36.1699, -115.1398),
(26, 26, 'admin.faye', 'house', 'sale', 320000, NULL, '2323 Ash St', 'Salt Lake City', '84101', 1850.75, 0.00, 'Modern home', 'Fireplace, Patio', TRUE, FALSE, 40.7608, -111.8910),
(27, 27, 'admin.gina', 'apartment', 'rent', 1600, 'Palm Towers', '2424 Palm Ln', 'Boise', '83701', 925.00, 1600.00, 'Urban apartment', 'Gym, Rooftop', TRUE, FALSE, 43.6150, -116.2023),
(28, 28, 'admin.hank', 'condo', 'sale', 210000, 'Magnolia Condos', '2525 Magnolia Dr', 'Helena', '59601', 1050.25, 0.00, 'Cozy condo', 'Parking, Security', TRUE, FALSE, 46.5891, -112.0391),
(29, 29, 'admin.iris', 'villa', 'rent', 2900, NULL, '2626 Palmwood Ave', 'Billings', '59101', 2400.50, 2900.00, 'Luxury villa', 'Pool, Deck', TRUE, FALSE, 45.7833, -108.5007),
(30, 30, 'admin.jake', 'room', 'rent', 700, 'Cherry Apartments', '2727 Cherry St', 'Anchorage', '99501', 340.75, 700.00, 'Shared room', 'Shared Bath', TRUE, TRUE, 61.2181, -149.9003);

-- Insert into SharedRoom (5 shared rooms for properties with sharing_allowed = TRUE)
INSERT INTO SharedRoom (room_id, property_id, monthly_rent, total_beds, available_beds, description) VALUES
(1, 5, 600.00, 2, 1, 'Cozy shared room in Portland'),
(2, 10, 700.00, 3, 2, 'Spacious shared room in Miami'),
(3, 15, 650.00, 2, 1, 'Shared room near downtown Raleigh'),
(4, 20, 800.00, 4, 3, 'Large shared room in Detroit'),
(5, 25, 750.00, 3, 2, 'Modern shared room in Las Vegas');

-- Insert into Receipt (10 receipts)
INSERT INTO Receipt (receipt_id, property_id, customer_id, amount, payment_status, payment_date) VALUES
(1, 1, 1, 1200.00, 'completed', '2025-03-01'),
(2, 3, 2, 1800.00, 'pending', '2025-03-02'),
(3, 5, 3, 600.00, 'completed', '2025-03-03'),
(4, 7, 4, 1500.00, 'failed', '2025-03-04'),
(5, 9, 5, 2500.00, 'completed', '2025-03-05'),
(6, 10, 6, 700.00, 'refunded', '2025-03-06'),
(7, 12, 7, 1300.00, 'completed', '2025-03-07'),
(8, 14, 8, 2800.00, 'pending', '2025-03-08'),
(9, 17, 9, 2000.00, 'completed', '2025-03-09'),
(10, 19, 10, 2700.00, 'completed', '2025-03-10');

-- Insert into Buy_Rent (10 relationships)
INSERT INTO Buy_Rent (customer_id, property_id) VALUES
(1, 1), (2, 3), (3, 5), (4, 7), (5, 9),
(6, 11), (7, 13), (8, 15), (9, 17), (10, 19);

-- Insert into Interested_In_Sharing (5 relationships)
INSERT INTO Interested_In_Sharing (customer_id, room_id) VALUES
(11, 1), (12, 2), (13, 3), (14, 4), (15, 5);

-- Insert into Participates (5 relationships)
INSERT INTO Participates (customer_id, room_id) VALUES
(16, 1), (17, 2), (18, 3), (19, 4), (20, 5);