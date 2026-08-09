from providers.angel.symbol_master_downloader import SymbolMasterDownloader
from symbols.symbol_master import SymbolMaster
from symbols.symbol_resolver import SymbolResolver

master = SymbolMaster()

count = SymbolMasterDownloader(master).download()

print(f"Loaded Symbols : {count}")

resolver = SymbolResolver(master)

reliance = resolver.resolve("RELIANCE")

print(reliance)
