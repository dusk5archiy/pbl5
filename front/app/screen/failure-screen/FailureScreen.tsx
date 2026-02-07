export default function FailureScreen(error?: any) {
  return (
    <div className="w-screen h-screen flex flex-col">
      <div className="w-full text-center text-[5vh] mt-[5vh] mb-[5vh]">
        Máy chủ gặp sự cố, vui lòng thử lại sau.
      </div>
      {
        error != null &&
        <div className="w-full text-center text-[5vh] mt-[5vh] mb-[5vh]">
          {error}
        </div>
      }
    </div>
  );
}
