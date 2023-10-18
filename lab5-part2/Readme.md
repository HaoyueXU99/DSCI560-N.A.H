

# Readme

This guide will walk you through the setup and execution of your web project. We will begin by setting up the Apache web server, followed by the installation of Node.js and other required tools. Lastly, we will initialize and run the provided application.

## Prerequisites:
- Ubuntu
- Root (sudo) privileges on the system

## Step-by-Step Guide:

### 1. Set Up Apache:

#### a. Start Apache service:

Initiate the Apache service to make it ready to serve web pages.

```bash
sudo systemctl start apache2
```

#### b. Test Apache:
Open your web browser and type in your server IP address. You should be greeted by Apache's default welcome page, indicating that the server is up and running.

#### c. Understanding Apache's Document Root:
By default, Apache serves files from `/var/www/html/`. This is where you can place your web files. 

If you wish to serve multiple websites or prefer a different directory, proceed to use VirtualHosts as explained in the next section.

#### d. Setting up VirtualHosts:
For example, to set up a new virtual host for a site:

- Apache's VirtualHosts feature allows you to host multiple websites on a single server. Each site can have its own configuration and directory.
  ```bash
  sudo mkdir /var/www/well_map.com
  ```

- **Directory Creation**: Start by creating a dedicated directory for your new website's files.

  ```bash
  sudo nano /etc/apache2/sites-available/well_map.com.conf
  ```

- **Configuration File**: For each site, a configuration file dictates how requests should be handled.

  ```apache
  <VirtualHost *:80>
      ServerAdmin webmaster@well_map.com
      ServerName well_map.com
      ServerAlias www.well_map.com
      DocumentRoot /var/www/well_map.com
      ErrorLog ${APACHE_LOG_DIR}/error.log
      CustomLog ${APACHE_LOG_DIR}/access.log combined
  </VirtualHost>
  ```

  Populate the file with the provided configuration, adjusting values like `ServerName` to match your domain name.

- **Activating the New Site**: Once set up, inform Apache about the new site and restart the service.

  ```bash
  sudo a2ensite well_map.com.conf
  sudo systemctl restart apache2
  ```

### 2. Configure Firewall:

If you're using UFW (Uncomplicated Firewall), which simplifies firewall management, you need to permit HTTP and HTTPS traffic for your Apache server to communicate with the outside world:
```bash
sudo ufw allow 'Apache Full'
```

### 3. Setting Up Node.js:

If you have older versions of node or nodejs installed, purge them:
```bash
sudo apt-get --purge remove node
sudo apt-get --purge remove nodejs
sudo apt-get autoremove
```

Install `curl` if not already installed:
```bash
sudo apt install curl
```

Add Node.js PPA for version 20.x and install:
```bash
curl -sL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verify Node.js and npm installation:
```bash
node -v
npm -v
```

Create a new OpenLayers application named `well-map` and start it:
```bash
sudo npm create ol-app well-map
cd well-map
sudo npm start
```

Set appropriate ownership for your website directory:
```bash
sudo chown -R haoyue:haoyue /var/www/well_map.com/
```

### 4. Update Your Web App:

Replace the contents of your web application with the provided files: 

- `index.html`
- `main.js`
- `style.css`

Additionally, add the following new files to your app:

- `data.csv`
- `store.py`
- `api_server.py`
- `oil-well.svg`

### 5. Installing Python Tools:

Update your package list and install pip for Python 3:
```bash
sudo apt update
sudo apt install python3-pip
```

Install necessary Python packages:
```bash
pip3 install pandas pymysql mysql-connector-python flask flask_cors
```

### 6. Run Python Scripts:

Execute the provided Python scripts:
```bash
python3 store.py
python3 api_server.py
```

![截屏2023-10-17 21.43.15](/Users/haoyuexu/Library/Application Support/typora-user-images/截屏2023-10-17 21.43.15.png)

 ![截屏2023-10-17 21.42.11](/Users/haoyuexu/Library/Application Support/typora-user-images/截屏2023-10-17 21.42.11.png)

![截屏2023-10-17 21.41.11](/Users/haoyuexu/Library/Application Support/typora-user-images/截屏2023-10-17 21.41.11.png)

### 7. Viewing Project:

Open your web browser and navigate to:
```
http://localhost:5173/
```
You should be able to see the result of your web application.
Note: It depends on the terminal information.

![截屏2023-10-17 21.45.26](/Users/haoyuexu/Library/Application Support/typora-user-images/截屏2023-10-17 21.45.26.png)