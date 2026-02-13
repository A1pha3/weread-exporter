import argparse
import asyncio
import logging
import os
import sys


def patch_windows():
    bin_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin", "win32")
    os.environ["PATH"] += ";" + bin_path
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(bin_path)  # type: ignore[attr-defined]


def patch_generateRequestHash():
    from pyppeteer import network_manager

    orig_generateRequestHash = network_manager.generateRequestHash

    def patched_generateRequestHash(request):
        request["headers"].pop("Origin", None)
        return orig_generateRequestHash(request)

    network_manager.generateRequestHash = patched_generateRequestHash


async def async_main():
    from . import export, utils, webpage

    parser = argparse.ArgumentParser(
        prog="weread-exporter", description="WeRead book export cmdline tool"
    )
    parser.add_argument("-b", "--book-id", help="book id")
    parser.add_argument(
        "-o",
        "--output-format",
        help="output file format",
        action="append",
        choices=["md", "epub", "pdf", "mobi", "txt"],
    )
    parser.add_argument(
        "--load-timeout",
        help="load chapter page timeout",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--load-interval",
        help="load chapter page interval time",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--css-file",
        help="overide default css style",
    )
    parser.add_argument(
        "--headless", help="chrome headless", action="store_true", default=False
    )
    parser.add_argument(
        "--force-login", help="force login first", action="store_true", default=False
    )
    parser.add_argument(
        "--use-default-profile",
        help="use default profile",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--mock-user-agent",
        help="use mock user-agent",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--proxy-server",
        help="http proxy server, e.g. http://127.0.0.1:8888",
    )
    parser.add_argument(
        "--list-ids",
        help="list book ids from booklist",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--list-booklists",
        help="list booklists for current user",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    args.output_format = args.output_format or ["epub"]
    if "mobi" in args.output_format and "epub" not in args.output_format:
        args.output_format.append("epub")

    if args.list_booklists:
        # 列出书单列表，无需 book-id
        page = webpage.WeReadWebPage(
            "home",
            cookie_path=os.path.join("cache", "cookie.txt"),
            webcache_path="cache",
        )
        page._home_url = webpage.WeReadWebPage.root_url
        try:
            await page.launch(
                headless=args.headless,
                force_login=args.force_login,
                use_default_profile=args.use_default_profile,
                mock_user_agent=args.mock_user_agent,
                proxy_server=args.proxy_server,
            )
            lists = await page.get_booklists()
            for it in lists:
                print("%s\t%s\t%s" % (it.get("title", ""), it["id"], it["url"]))
        finally:
            await page.close()
        return 0

    if not args.book_id:
        raise RuntimeError("Missing required option: --book-id")

    extra_css = None
    if args.css_file:
        if not os.path.isfile(args.css_file):
            raise RuntimeError("CSS file %s not exist" % args.css_file)
        with open(args.css_file) as fp:
            extra_css = fp.read()

    if "_" in args.book_id:
        # book list id
        if args.list_ids:
            for it in await utils.get_book_list_full(args.book_id):
                print("%s\t%s\t%s" % (it["title"], it["original_id"], it["hashed_id"]))
            return 0
        book_list = [it["id"] for it in await utils.get_book_list(args.book_id)]
    else:
        book_list = [args.book_id]

    for book_id in book_list:
        logging.info("Exporting book %s" % book_id)
        page = webpage.WeReadWebPage(
            book_id,
            cookie_path=os.path.join("cache", "cookie.txt"),
            webcache_path="cache",
        )
        if not await page.check_valid():
            logging.warning("Book %s status is invalid, stop exporting" % book_id)
            continue
        save_path = os.path.join("cache", book_id)
        output_dir = "output"
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        exporter = export.WeReadExporter(page, save_path)
        while True:
            try:
                await page.launch(
                    headless=args.headless,
                    force_login=args.force_login,
                    use_default_profile=args.use_default_profile,
                    mock_user_agent=args.mock_user_agent,
                    proxy_server=args.proxy_server,
                )
            except RuntimeError:
                logging.exception("Launch book %s home page failed" % book_id)
                await asyncio.sleep(2)
                continue

            try:
                await exporter.export_markdown(args.load_timeout, args.load_interval)
            except utils.LoadChapterFailedError:
                logging.warning("Load chapter failed, close browser and retry")
                await page.close()
            else:
                await page.close()
                break

        await exporter.pre_process_markdown()
        title = await exporter.get_book_title()
        title = utils.format_filename(title)

        if "epub" in args.output_format:
            _save_path = os.path.join(output_dir, "%s.epub" % title)
            if os.path.isfile(_save_path):
                logging.info("File %s exist, ignore export" % _save_path)
            else:
                await exporter.markdown_to_epub(_save_path, extra_css=extra_css)
                logging.info("Save file %s complete" % _save_path)

        if "md" in args.output_format:
            _save_path = os.path.join(output_dir, "%s.md" % title)
            if os.path.isfile(_save_path):
                logging.info("File %s exist, ignore export" % _save_path)
            else:
                await exporter.merge_markdown(_save_path)
                logging.info("Save file %s complete" % _save_path)

        if "pdf" in args.output_format:
            _save_path = os.path.join(output_dir, "%s.pdf" % title)
            if os.path.isfile(_save_path):
                logging.info("File %s exist, ignore export" % _save_path)
            else:
                image_format = "jpg"
                if sys.platform == "win32":
                    image_format = "png"
                await exporter.markdown_to_pdf(
                    _save_path,
                    extra_css=extra_css,
                    image_format=image_format,
                )
                logging.info("Save file %s complete" % _save_path)

        if "mobi" in args.output_format:
            if sys.platform != "linux":
                logging.error("Only linux system supported to export mobi format")
                return -1
            epub_path = os.path.join(output_dir, "%s.epub" % title)
            _save_path = os.path.join(output_dir, "%s.mobi" % title)
            if os.path.isfile(_save_path):
                logging.info("File %s exist, ignore export" % _save_path)
            else:
                await exporter.epub_to_mobi(epub_path, _save_path)
                if not os.path.isfile(_save_path):
                    logging.warning("Create mobi file failed")
                    continue
                logging.info("Save file %s complete" % _save_path)

        if "txt" in args.output_format:
            _save_path = os.path.join(output_dir, "%s.txt" % title)
            if os.path.isfile(_save_path):
                logging.info("File %s exist, ignore export" % _save_path)
            else:
                await exporter.markdown_to_txt(_save_path)
                logging.info("Save file %s complete" % _save_path)
    return 0


def main():
    if sys.platform == "win32":
        patch_windows()
    patch_generateRequestHash()
    logging.root.level = logging.INFO
    handler = logging.StreamHandler()
    fmt = "[%(asctime)s][%(levelname)s]%(message)s"
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_main())
    except Exception as e:
        logging.error("Fatal error in main program: %s" % str(e))
        import traceback

        traceback.print_exc()
        return 1  # 返回非零退出码


if __name__ == "__main__":
    main()
