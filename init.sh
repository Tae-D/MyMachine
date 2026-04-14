npm run start &
cd ./CocktailPi/backend
mvn spring-boot:run &
sleep 5
chromium http://localhost:3000 --kiosk  