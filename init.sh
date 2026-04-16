npm run start &
cd CocktailPi/backend
mvn spring-boot:run &
cd ../frontend
npm run dev &
DISPLAY=:0 chromium http://localhost:3000 --kiosk --password-store=basic