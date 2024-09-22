pip3 install -r requirements.txt
playwright install
go install github.com/projectdiscovery/katana/cmd/katana@latest
curl -sfL https://raw.githubusercontent.com/Bearer/bearer/main/contrib/install.sh | sh