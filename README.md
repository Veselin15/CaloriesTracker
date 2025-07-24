---

## Environment Variables

The project uses [python-dotenv](https://pypi.org/project/python-dotenv/) to load environment variables from a `.env` file.  
**Never commit your `.env` file or secrets to version control.**

---

## Deployment

- The app is deployed on [Render](https://render.com/).
- Static and media files are served using Django's configuration.
- Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `settings.py` for your deployment domain.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [FatSecret API](https://platform.fatsecret.com/api/)
- [Render](https://render.com/)

---

## Contact

For questions or support, open an issue or contact [your-email@example.com](mailto:your-email@example.com).
