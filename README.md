# MBTA Explorer
Sample code exercising the MBTA API. See the deployed service at https://mbta.mcgachey.org.

## Technologies
The MBTA Explorer code uses the following technologies:
- A [Python/Flask](https://flask.palletsprojects.com/en/2.0.x/) backend.
- Python's [Requests](https://docs.python-requests.org/en/master/index.html) library to access the MBTA API.
- The [Responses](https://github.com/getsentry/responses) library to mock elements of the Requests library.
- [Bootstrap](https://getbootstrap.com/) with [JQuery](https://jquery.com/) to present user interface elements.
- The [DataTables](https://www.datatables.net/) library to present, sort and filter tabular data.
- [FontAwesome](https://fontawesome.com/) for icons and logos.
- The [Google Maps Embed API](https://developers.google.com/maps/documentation/embed/get-started) to present Streetview images of each MBTA stop.

The deployment stack includes:
- Hosted on an AWS [Lightsail](https://aws.amazon.com/lightsail/) instance, running [Ubuntu 20.04](http://www.releases.ubuntu.com/20.04/).
- Lightsail manages the server's static IP and DNS records.
- An SSL certificate from [Let's Encrypt](https://letsencrypt.org/).
- The [Gunicorn](https://gunicorn.org/) WSGI server.
- The [Nginx](https://nginx.org/en/) reverse proxy.

## Deployment Instructions
Deployment is performed using the `bin/server_init.sh` script. 

Keys and secrets are not checked into Git. A secrets file is manually copied to the server and called by the 
`bin/run_service.sh` script prior to launching the Gunicorn process. This file sets environment variables to the secret
values, which are then read by the service code. A template for this file can be seen in the `secure.sh.example` file.

## Project Notes
In order to stay (close to) the suggested time range for the project, I made some compromises.

#### Technology
- I considered using Docker and Elastic Beanstalk rather than Lightsail in order to get closer to what would be used in
  production. I didn't go that way for two reasons:
    - My experience with EB in particular is fairly limited and dated, so I'd want to spend more time than is available
      to get more familiar with it
    - I already had a Lightsail account set up with a TLD registered, billing established and so on, so it was quicker
      to get started.
  
### Deployment
- In production, I would use an established Infrastructure as Code framework rather than individual scripts. As above -
  it's been a while since I used Terraform or CloudFormation, so I went with the simpler route rather than getting back
  up to speed on one of those stacks.

- A consequence of the deploy script approach is that the domain name is hard-coded in the setup scripts. Given more
  time I'd rather use a framework that would let me pull it out to a variable.

- Updating code on the server is pretty manual for now; I SSH into the Lightsail server, git pull, then restart the
  service. For production, a better CI/CD system would be needed.

- Log messages are just going to syslog. There are plenty of better options, but this will do for now.

### Application
- Presenting errors to users is pretty rudimentary; on an unexpected API response or server error the user sees a fairly
  basic page that includes an error ID. The error ID is included in the logs allowing for some level of debugging.

- Test coverage is low. I've included a bare minimum of unit tests to show how they would be implemented, but for 
  production I'd want to do a lot more testing (with separate smoke and performance test suites).
