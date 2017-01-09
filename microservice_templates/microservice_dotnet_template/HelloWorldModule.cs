using Nancy;
namespace _MICROSERVICE_DOTNET_TEMPLATE_
{
    public class HomeModule : NancyModule
    {
        public HomeModule()
        {
            Get("/", args => "Hello, World!");
        }
    }
}
